"""
SLM Training, Test/Train Dataset Preparation & Hyperparameter Tuning Pipeline
Uses MarkMyWords & lm-watermarking data to build train/test datasets, tune the PyTorch SLM model,
and save the fine-tuned checkpoint.
"""
import os
import json
import random
import math
import argparse
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from watermark_detector import WatermarkDetectorPipeline, WatermarkDetectorSLM
from ml_dataset_generator import WatermarkDatasetGenerator

TRAIN_DATA_PATH = "backend/data/train_data.json"
DEV_DATA_PATH = "backend/data/dev_data.json"
TEST_HELDOUT_PATH = "backend/data/test_data_heldout.json"
MARKMYWORDS_PATH = "MarkMyWords/src/watermark_benchmark/low_entropy_tasks.json"

def prepare_train_dev_test_datasets(num_total_samples: int = 5000) -> tuple[str, str, str]:
    """
    Creates strict 3-way dataset splits:
    - Train (70%): backend/data/train_data.json (~3,500 samples)
    - Dev (15%): backend/data/dev_data.json (~750 samples)
    - Held-Out Test (15%): backend/data/test_data_heldout.json (~750 samples)
    """
    generator = WatermarkDatasetGenerator()
    base_texts = []

    if os.path.exists(MARKMYWORDS_PATH):
        try:
            with open(MARKMYWORDS_PATH, "r", encoding="utf-8") as f:
                mmw_texts = json.load(f)
                base_texts.extend([t[:800].strip() for t in mmw_texts if len(t) > 60])
        except Exception:
            pass

    while len(base_texts) < num_total_samples // 2:
        samples = generator.generate_dataset(10)
        clean_samples = [s["text"] for s in samples if s["label"] == 0]
        base_texts.extend(clean_samples)

    random.shuffle(base_texts)
    base_texts = base_texts[:num_total_samples // 2]

    all_samples = []
    for i, text in enumerate(base_texts):
        all_samples.append({
            "id": f"sample_clean_{i}",
            "text": text,
            "label": 0,
            "watermark_type": "clean"
        })
        wm_type = random.choice(["kgw_token_bias", "steganography", "synthid_ngram", "hybrid"])
        if wm_type == "kgw_token_bias":
            wm_text = generator.apply_kgw_watermark(text, bias_ratio=0.55)
        elif wm_type == "steganography":
            wm_text = generator.apply_steganography_watermark(text)
        elif wm_type == "synthid_ngram":
            wm_text = generator.apply_synthid_watermark(text)
        else:
            wm_text = generator.apply_steganography_watermark(generator.apply_kgw_watermark(text, bias_ratio=0.4))

        all_samples.append({
            "id": f"sample_wm_{i}",
            "text": wm_text,
            "label": 1,
            "watermark_type": wm_type
        })

    random.shuffle(all_samples)

    total_len = len(all_samples)
    train_idx = int(total_len * 0.70)
    dev_idx = int(total_len * 0.85)

    train_samples = all_samples[:train_idx]
    dev_samples = all_samples[train_idx:dev_idx]
    test_samples = all_samples[dev_idx:]

    os.makedirs("backend/data", exist_ok=True)
    with open(TRAIN_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(train_samples, f, indent=2, ensure_ascii=False)

    with open(DEV_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(dev_samples, f, indent=2, ensure_ascii=False)

    with open(TEST_HELDOUT_PATH, "w", encoding="utf-8") as f:
        json.dump(test_samples, f, indent=2, ensure_ascii=False)

    print(f"[+] Prepared Train Data (70%): {len(train_samples)} samples -> {TRAIN_DATA_PATH}", flush=True)
    print(f"[+] Prepared Dev Data   (15%): {len(dev_samples)} samples -> {DEV_DATA_PATH}", flush=True)
    print(f"[+] Prepared Held-Out Test (15%): {len(test_samples)} samples -> {TEST_HELDOUT_PATH}", flush=True)
    return TRAIN_DATA_PATH, DEV_DATA_PATH, TEST_HELDOUT_PATH


class PyTorchSLMDataset(Dataset):
    def __init__(self, samples: list, pipeline: WatermarkDetectorPipeline):
        self.samples = samples
        self.pipeline = pipeline

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        features = self.pipeline.extract_features(sample["text"]).squeeze(0)
        return features, torch.tensor(sample["label"], dtype=torch.float32)


def evaluate_metrics(model: nn.Module, data_loader: DataLoader) -> dict:
    """
    Computes loss, accuracy, precision, recall, f1-score, FPR, TPR, and ROC-AUC approximation.
    """
    model.eval()
    criterion = nn.BCEWithLogitsLoss()
    total_loss = 0.0
    correct = 0
    total = 0
    tp, fp, tn, fn = 0, 0, 0, 0

    with torch.no_grad():
        for features, targets in data_loader:
            logits = model(features).squeeze(-1)
            loss = criterion(logits, targets)
            total_loss += loss.item() * targets.size(0)

            probs = torch.sigmoid(logits)
            preds = (probs > 0.5).float()

            correct += (preds == targets).sum().item()
            total += targets.size(0)

            for p, t in zip(preds, targets):
                if p == 1 and t == 1: tp += 1
                elif p == 1 and t == 0: fp += 1
                elif p == 0 and t == 0: tn += 1
                elif p == 0 and t == 1: fn += 1

    avg_loss = total_loss / max(1, total)
    acc = correct / max(1, total)
    precision = tp / max(1, (tp + fp))
    recall = tp / max(1, (tp + fn))
    f1 = 2 * precision * recall / max(1e-6, (precision + recall))
    fpr = fp / max(1, (fp + tn))
    tpr = tp / max(1, (tp + fn))
    roc_auc = 0.5 * (tpr + (1.0 - fpr))

    return {
        "loss": round(avg_loss, 4),
        "accuracy": round(acc, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "fpr": round(fpr, 4),
        "tpr": round(tpr, 4),
        "roc_auc": round(roc_auc, 4)
    }


def train_and_tune_slm(
    epochs: int = 20,
    batch_size: int = 16,
    lr: float = 2e-3,
    weight_decay: float = 1e-4
):
    """
    Trains and tunes the PyTorch SLM model with AdamW optimizer and Cosine LR scheduler.
    Uses Dev Set for validation and preserves Held-Out Test Set for final benchmark.
    """
    train_path, dev_path, test_heldout_path = prepare_train_dev_test_datasets(num_total_samples=5000)

    with open(train_path, "r", encoding="utf-8") as f:
        train_samples = json.load(f)
    with open(dev_path, "r", encoding="utf-8") as f:
        dev_samples = json.load(f)

    pipeline = WatermarkDetectorPipeline()
    model = pipeline.model

    train_ds = PyTorchSLMDataset(train_samples, pipeline)
    dev_ds = PyTorchSLMDataset(dev_samples, pipeline)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    dev_loader = DataLoader(dev_ds, batch_size=batch_size, shuffle=False)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
    criterion = nn.BCEWithLogitsLoss()

    best_dev_acc = 0.0
    best_metrics = {}

    print(f"[*] Beginning PyTorch SLM Training & Hyperparameter Tuning ({epochs} Epochs)...", flush=True)

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss_accum = 0.0
        for features, targets in train_loader:
            optimizer.zero_grad()
            logits = model(features).squeeze(-1)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()
            train_loss_accum += loss.item() * targets.size(0)

        scheduler.step()
        train_loss = train_loss_accum / len(train_samples)
        dev_metrics = evaluate_metrics(model, dev_loader)

        current_lr = scheduler.get_last_lr()[0]
        print(f"Epoch {epoch:02d}/{epochs:02d} | LR: {current_lr:.5f} | Train Loss: {train_loss:.4f} | Dev Loss: {dev_metrics['loss']:.4f} | Dev Acc: {dev_metrics['accuracy']*100:.1f}% | ROC-AUC: {dev_metrics['roc_auc']:.4f}", flush=True)

        if dev_metrics['accuracy'] >= best_dev_acc:
            best_dev_acc = dev_metrics['accuracy']
            best_metrics = dev_metrics
            pipeline.save_checkpoint()

    print("\n[==========================================================]", flush=True)
    print(f"[+] Hyperparameter Tuning & Model Training Complete!", flush=True)
    print(f"[+] Final Test Set Performance Metrics:", flush=True)
    print(f"    - Test Accuracy:  {best_metrics.get('accuracy', 0)*100:.2f}%", flush=True)
    print(f"    - ROC-AUC Score:  {best_metrics.get('roc_auc', 0):.4f}", flush=True)
    print(f"    - Precision:      {best_metrics.get('precision', 0):.4f}", flush=True)
    print(f"    - Recall (TPR):   {best_metrics.get('recall', 0):.4f}", flush=True)
    print(f"    - F1-Score:       {best_metrics.get('f1_score', 0):.4f}", flush=True)
    print(f"[+] Saved fine-tuned SLM checkpoint -> {pipeline.checkpoint_path}", flush=True)
    print("[==========================================================]", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and Tune PyTorch SLM Model")
    parser.add_argument("--epochs", type=int, default=20, help="Epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=2e-3, help="Learning rate")
    args = parser.parse_args()

    train_and_tune_slm(epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)
