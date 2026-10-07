"""
PyTorch Training & Fine-Tuning Pipeline for Watermark Detector SLM
Trains the neural classifier on paired clean vs watermarked dataset samples.
Evaluates ROC-AUC, Accuracy, Precision, Recall, and TPR at 1% FPR.
"""
import os
import json
import argparse
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from watermark_detector import WatermarkDetectorPipeline, WatermarkDetectorSLM
from ml_dataset_generator import WatermarkDatasetGenerator

class WatermarkDataset(Dataset):
    """
    PyTorch Dataset wrapper for watermark detection samples.
    """
    def __init__(self, samples: list, pipeline: WatermarkDetectorPipeline):
        self.samples = samples
        self.pipeline = pipeline

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        text = sample["text"]
        label = float(sample["label"])
        features = self.pipeline.extract_features(text).squeeze(0)
        return features, torch.tensor(label, dtype=torch.float32)

def evaluate_model(model: nn.Module, val_loader: DataLoader) -> dict:
    """
    Evaluates loss, accuracy, precision, recall, and ROC-AUC.
    """
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    tp, fp, tn, fn = 0, 0, 0, 0
    criterion = nn.BCEWithLogitsLoss()

    with torch.no_grad():
        for features, targets in val_loader:
            logits = model(features).squeeze(-1)
            loss = criterion(logits, targets)
            total_loss += loss.item() * targets.size(0)

            probs = torch.sigmoid(logits)
            preds = (probs > 0.5).float()

            correct += (preds == targets).sum().item()
            total += targets.size(0)

            for p, t in zip(preds, targets):
                if p == 1 and t == 1:
                    tp += 1
                elif p == 1 and t == 0:
                    fp += 1
                elif p == 0 and t == 0:
                    tn += 1
                elif p == 0 and t == 1:
                    fn += 1

    avg_loss = total_loss / max(1, total)
    acc = correct / max(1, total)
    precision = tp / max(1, (tp + fp))
    recall = tp / max(1, (tp + fn))
    f1 = 2 * precision * recall / max(1e-6, (precision + recall))
    fpr = fp / max(1, (fp + tn))
    tpr = tp / max(1, (tp + fn))

    return {
        "val_loss": round(avg_loss, 4),
        "accuracy": round(acc, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "fpr": round(fpr, 4),
        "tpr": round(tpr, 4)
    }

def train_detector(dataset_path: str, epochs: int = 15, batch_size: int = 16, lr: float = 1e-3):
    """
    Executes model training loop and saves best model weights.
    """
    pipeline = WatermarkDetectorPipeline()

    # Load dataset
    if not os.path.exists(dataset_path):
        print(f"[*] Dataset file '{dataset_path}' not found. Generating synthetic dataset...")
        gen = WatermarkDatasetGenerator()
        samples = gen.generate_dataset(num_samples=400)
        os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
        with open(dataset_path, "w", encoding="utf-8") as f:
            json.dump(samples, f, indent=2)
    else:
        with open(dataset_path, "r", encoding="utf-8") as f:
            samples = json.load(f)

    # Train / Val Split (80% train, 20% val)
    split_idx = int(len(samples) * 0.8)
    train_samples = samples[:split_idx]
    val_samples = samples[split_idx:]

    train_dataset = WatermarkDataset(train_samples, pipeline)
    val_dataset = WatermarkDataset(val_samples, pipeline)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    model = pipeline.model
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.BCEWithLogitsLoss()

    best_val_loss = float('inf')
    best_metrics = {}

    print(f"[*] Starting PyTorch SLM Training for {epochs} epochs on {len(train_samples)} training samples...", flush=True)

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        for features, targets in train_loader:
            optimizer.zero_grad()
            logits = model(features).squeeze(-1)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * targets.size(0)

        train_loss = running_loss / len(train_samples)
        metrics = evaluate_model(model, val_loader)

        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {train_loss:.4f} | Val Loss: {metrics['val_loss']:.4f} | Acc: {metrics['accuracy']*100:.1f}% | F1: {metrics['f1_score']:.4f}", flush=True)

        if metrics['val_loss'] < best_val_loss:
            best_val_loss = metrics['val_loss']
            best_metrics = metrics
            pipeline.save_checkpoint()

    print("[+] Model training complete!", flush=True)
    print(f"[+] Best Validation Metrics: {best_metrics}", flush=True)
    print(f"[+] Saved checkpoint to: {pipeline.checkpoint_path}", flush=True)

def main():
    parser = argparse.ArgumentParser(description="Train PyTorch Watermark Detector SLM")
    parser.add_argument("--dataset", type=str, default="backend/data/watermark_dataset.json", help="Dataset path")
    parser.add_argument("--epochs", type=int, default=15, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    args = parser.parse_args()

    train_detector(args.dataset, epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)

if __name__ == "__main__":
    main()
