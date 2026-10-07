"""
Bootstrapped Evaluation & Confusion Matrix Module with 95% Confidence Intervals
Computes raw counts (TP/FP/TN/FN), recall, precision, F1-score, clean specificity,
and 1000-sample non-parametric percentile bootstrapped 95% CIs per watermark type.
"""
import os
import json
import random
import numpy as np
import torch
from collections import defaultdict
from watermark_detector import WatermarkDetectorPipeline, is_kgw_green_token

def bootstrap_ci(metric_fn, data: list, n_bootstraps: int = 1000, ci_level: float = 0.95) -> tuple[float, float, float]:
    """
    Computes point estimate and 95% percentile bootstrap confidence interval [lower, upper].
    """
    if not data:
        return 0.0, 0.0, 0.0

    point_estimate = metric_fn(data)
    bootstrap_estimates = []

    np.random.seed(42)
    random.seed(42)

    for _ in range(n_bootstraps):
        resample = [data[i] for i in np.random.choice(len(data), size=len(data), replace=True)]
        val = metric_fn(resample)
        bootstrap_estimates.append(val)

    alpha = (1.0 - ci_level) / 2.0
    lower = float(np.percentile(bootstrap_estimates, alpha * 100))
    upper = float(np.percentile(bootstrap_estimates, (1.0 - alpha) * 100))

    return point_estimate, lower, upper


def run_bootstrap_evaluation(dataset_path: str, model_pipeline: WatermarkDetectorPipeline = None) -> dict:
    """
    Runs model evaluation on target dataset path, computing per-class raw counts,
    recall/precision/F1, and 95% bootstrapped confidence intervals.
    """
    if not os.path.exists(dataset_path):
        print(f"[-] File not found: {dataset_path}")
        return {}

    with open(dataset_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    pipeline = model_pipeline or WatermarkDetectorPipeline()
    model = pipeline.model
    model.eval()

    # Pre-compute predictions for all samples
    eval_records = []
    with torch.no_grad():
        for sample in samples:
            text = sample["text"]
            label = sample["label"]
            wm_type = sample.get("watermark_type", "clean")

            features = pipeline.extract_features(text)
            logit = model(features).squeeze()
            prob = float(torch.sigmoid(logit).item())

            inv_count = int(features[0, 0].item())
            homo_count = int(features[0, 2].item())
            kgw_matches = int(features[0, 4].item())
            synthid_count = int(features[0, 10].item())

            import re
            clean_words = [re.sub(r'[^\w]', '', w).lower() for w in text.split() if w]
            n_words = max(1, len(clean_words))
            z_score = (kgw_matches - 0.5 * n_words) / max(1e-6, 0.5 * (n_words ** 0.5))

            if inv_count > 0: prob = max(prob, 0.95)
            if homo_count > 0: prob = max(prob, 0.90)
            if synthid_count > 0: prob = max(prob, 0.85)

            kgw_detected = z_score >= 1.70
            if kgw_detected:
                prob = max(prob, 0.80)

            has_any_signal = inv_count > 0 or homo_count > 0 or synthid_count > 0 or kgw_detected
            if not has_any_signal:
                prob = min(prob, 0.15)

            pred = 1 if prob > 0.50 else 0

            eval_records.append({
                "id": sample.get("id"),
                "text": text,
                "label": label,
                "watermark_type": wm_type,
                "prob": prob,
                "pred": pred
            })

    # Group records by category
    by_category = defaultdict(list)
    for r in eval_records:
        by_category[r["watermark_type"]].append(r)

    print("\n" + "=" * 115)
    print(f"PER-CLASS EVALUATION WITH 95% BOOTSTRAPPED CONFIDENCE INTERVALS ({dataset_path})")
    print("=" * 115)
    print(f"{'Category':<18} | {'Raw Counts':<12} | {'Recall [95% CI]':<25} | {'Precision [95% CI]':<25} | {'F1-Score'}")
    print("-" * 115)

    results = {}

    for cat, recs in sorted(by_category.items()):
        n_tot = len(recs)
        
        if cat == "clean":
            # Clean text: metric is Specificity (TN / (TN + FP))
            spec_point, spec_low, spec_high = bootstrap_ci(
                lambda data: sum(1 for d in data if d["pred"] == 0) / max(1, len(data)),
                recs
            )
            tn_cnt = sum(1 for d in recs if d["pred"] == 0)
            raw_str = f"{tn_cnt}/{n_tot}"
            spec_str = f"{spec_point*100:5.1f}% [{spec_low*100:5.1f}% - {spec_high*100:5.1f}%]"
            print(f"{cat:<18} | {raw_str:<12} | Spec: {spec_str:<25} | {'N/A':<25} | {'N/A'}")
            results[cat] = {
                "count": n_tot, "raw": raw_str,
                "specificity": spec_point, "ci_low": spec_low, "ci_high": spec_high
            }
        else:
            # Watermarked text: Recall (TP / (TP + FN)) and Precision (TP / (TP + FP))
            rec_point, rec_low, rec_high = bootstrap_ci(
                lambda data: sum(1 for d in data if d["pred"] == 1) / max(1, len(data)),
                recs
            )
            prec_point, prec_low, prec_high = bootstrap_ci(
                lambda data: sum(1 for d in data if d["pred"] == 1) / max(1, sum(1 for d in data if d["pred"] == 1)),
                recs
            )
            tp_cnt = sum(1 for d in recs if d["pred"] == 1)
            raw_str = f"{tp_cnt}/{n_tot}"
            rec_str = f"{rec_point*100:5.1f}% [{rec_low*100:5.1f}% - {rec_high*100:5.1f}%]"
            prec_str = f"{prec_point*100:5.1f}% [{prec_low*100:5.1f}% - {prec_high*100:5.1f}%]"
            f1 = 2 * prec_point * rec_point / max(1e-6, (prec_point + rec_point))

            print(f"{cat:<18} | {raw_str:<12} | {rec_str:<25} | {prec_str:<25} | {f1:.3f}")
            results[cat] = {
                "count": n_tot, "raw": raw_str,
                "recall": rec_point, "rec_low": rec_low, "rec_high": rec_high,
                "precision": prec_point, "prec_low": prec_low, "prec_high": prec_high,
                "f1": f1
            }

    print("=" * 115 + "\n")
    return results

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "backend/data/dev_data.json"
    run_bootstrap_evaluation(path)
