"""
Per-Watermark-Type Evaluation & Confusion Matrix Diagnostic Script
Evaluates the PyTorch SLM Watermark Detector across specific watermark categories:
- kgw_token_bias
- steganography
- synthid_ngram
- hybrid
- clean
No retraining required — evaluates current model checkpoint on backend/data/test_data.json.
"""
import os
import json
import torch
from collections import defaultdict
from watermark_detector import WatermarkDetectorPipeline

TEST_HELDOUT_PATH = "backend/data/test_data_heldout.json"
DEV_DATA_PATH = "backend/data/dev_data.json"

def evaluate_per_class_performance(test_data_path: str = TEST_HELDOUT_PATH):
    """
    Evaluates detector performance per watermark type and outputs complete confusion matrix metrics.
    """
    if not os.path.exists(test_data_path):
        print(f"[-] Evaluation file '{test_data_path}' not found.")
        return

    with open(test_data_path, "r", encoding="utf-8") as f:
        test_samples = json.load(f)

    pipeline = WatermarkDetectorPipeline()
    model = pipeline.model
    model.eval()

    print(f"[*] Running Per-Class Evaluation on {len(test_samples)} Samples ({test_data_path})...", flush=True)

    # Group metrics by watermark_type
    stats = defaultdict(lambda: {"count": 0, "tp": 0, "fp": 0, "tn": 0, "fn": 0, "risk_scores": []})

    with torch.no_grad():
        for sample in test_samples:
            text = sample["text"]
            label = sample["label"] # 0=clean, 1=watermarked
            wm_type = sample.get("watermark_type", "clean")

            features = pipeline.extract_features(text)
            logit = model(features).squeeze()
            prob = float(torch.sigmoid(logit).item())
            
            # Combine neural prob with heuristics
            inv_count = int(features[0, 0].item())
            homo_count = int(features[0, 2].item())
            if inv_count > 0: prob = max(prob, 0.95)
            if homo_count > 0: prob = max(prob, 0.90)

            pred = 1 if prob > 0.45 else 0

            s = stats[wm_type]
            s["count"] += 1
            s["risk_scores"].append(prob * 100.0)

            if label == 1:
                if pred == 1: s["tp"] += 1
                else: s["fn"] += 1
            else:
                if pred == 0: s["tn"] += 1
                else: s["fp"] += 1

    print("\n" + "=" * 95)
    print(f"{'Watermark Category':<20} | {'Count':<5} | {'Recall':<9} | {'Precision':<10} | {'F1-Score':<9} | {'Avg Risk %':<10} | {'Status'}")
    print("=" * 95)

    overall_tp, overall_fp, overall_tn, overall_fn = 0, 0, 0, 0

    for wm_type, s in sorted(stats.items()):
        cnt = s["count"]
        tp, fp, tn, fn = s["tp"], s["fp"], s["tn"], s["fn"]
        overall_tp += tp
        overall_fp += fp
        overall_tn += tn
        overall_fn += fn

        avg_risk = sum(s["risk_scores"]) / max(1, cnt)

        if wm_type == "clean":
            specificity = tn / max(1, (tn + fp))
            print(f"{wm_type:<20} | {cnt:<5} | {specificity*100:8.1f}% | {'N/A':<10} | {'N/A':<9} | {avg_risk:8.1f}%  | {'Baseline Spec: ' + str(round(specificity*100, 1)) + '%'}")
        else:
            recall = tp / max(1, (tp + fn))
            precision = tp / max(1, (tp + fp)) if (tp + fp) > 0 else 0.0
            f1 = 2 * precision * recall / max(1e-6, (precision + recall))
            status_flag = "[WEAK RECALL]" if recall < 0.70 else "[STRONG]"
            print(f"{wm_type:<20} | {cnt:<5} | {recall*100:8.1f}% | {precision*100:9.1f}% | {f1:8.3f} | {avg_risk:8.1f}%  | {status_flag}")

    print("=" * 95)
    total_samples = len(test_samples)
    overall_acc = (overall_tp + overall_tn) / max(1, total_samples)
    overall_recall = overall_tp / max(1, (overall_tp + overall_fn))
    overall_precision = overall_tp / max(1, (overall_tp + overall_fp)) if (overall_tp + overall_fp) > 0 else 0.0
    overall_f1 = 2 * overall_precision * overall_recall / max(1e-6, (overall_precision + overall_recall))

    print(f"Overall Accuracy:  {overall_acc*100:.2f}%")
    print(f"Overall Recall:    {overall_recall*100:.2f}%")
    print(f"Overall Precision: {overall_precision*100:.2f}%")
    print(f"Overall F1-Score:  {overall_f1:.4f}")
    print("=" * 95 + "\n")

if __name__ == "__main__":
    evaluate_per_class_performance()
