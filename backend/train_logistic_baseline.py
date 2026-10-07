"""
Logistic Regression Baseline Model Comparison Script
Trains plain Logistic Regression (sklearn.linear_model.LogisticRegression) on the exact same
feature vectors and evaluates on backend/data/test_data_heldout.json with 95% bootstrapped CIs.
"""
import os
import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from watermark_detector import WatermarkDetectorPipeline
from eval_bootstrap import bootstrap_ci

TRAIN_DATA_PATH = "backend/data/train_data.json"
TEST_HELDOUT_PATH = "backend/data/test_data_heldout.json"

import hashlib

def run_logistic_regression_baseline():
    pipeline = WatermarkDetectorPipeline()
    pytorch_model = pipeline.model
    pytorch_model.eval()

    # 1. Print model object hash & weight checksum
    model_obj_id = id(pytorch_model)
    weight_bytes = b"".join([p.data.numpy().tobytes() for p in pytorch_model.parameters()])
    weight_md5 = hashlib.md5(weight_bytes).hexdigest()
    print(f"[+] PyTorch SLM Model Object ID: {model_obj_id}")
    print(f"[+] PyTorch SLM Weight Checksum (MD5): {weight_md5}")

    # Load train data
    with open(TRAIN_DATA_PATH, "r", encoding="utf-8") as f:
        train_samples = json.load(f)

    # Load test data
    with open(TEST_HELDOUT_PATH, "r", encoding="utf-8") as f:
        test_samples = json.load(f)

    print("[*] Extracting feature vectors for Logistic Regression Baseline...", flush=True)
    X_train, y_train = [], []
    for s in train_samples:
        feats = pipeline.extract_features(s["text"]).squeeze(0).numpy()
        X_train.append(feats)
        y_train.append(s["label"])

    X_test, y_test = [], []
    for s in test_samples:
        feats = pipeline.extract_features(s["text"]).squeeze(0).numpy()
        X_test.append(feats)
        y_test.append(s["label"])

    X_train, y_train = np.array(X_train), np.array(y_train)
    X_test, y_test = np.array(X_test), np.array(y_test)

    # Fit Logistic Regression baseline
    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(X_train, y_train)
    logreg_obj_id = id(clf)
    print(f"[+] Logistic Regression Object ID: {logreg_obj_id}")

    logreg_probs = clf.predict_proba(X_test)[:, 1]
    logreg_preds = (logreg_probs > 0.50).astype(int)

    # Pure PyTorch Model Inference
    import torch
    with torch.no_grad():
        pytorch_logits = pytorch_model(torch.tensor(X_test, dtype=torch.float32)).squeeze(-1)
        pytorch_probs = torch.sigmoid(pytorch_logits).numpy()
        pytorch_preds = (pytorch_probs > 0.50).astype(int)

    # Compare predictions on first 50 samples
    agree_count = sum(1 for p1, p2 in zip(pytorch_preds, logreg_preds) if p1 == p2)
    print(f"[+] Side-by-Side Inference Agreement on {len(test_samples)} Held-Out Samples: {agree_count}/{len(test_samples)} ({agree_count/len(test_samples)*100:.1f}%)")

    print("\n" + "=" * 90)
    print(f"{'Sample ID':<15} | {'Label':<6} | {'Category':<16} | {'PyTorch Prob':<12} | {'LogReg Prob':<12} | {'Match?'}")
    print("=" * 90)
    for i in range(min(30, len(test_samples))):
        s = test_samples[i]
        p_prob = pytorch_probs[i]
        l_prob = logreg_probs[i]
        match_str = "YES" if pytorch_preds[i] == logreg_preds[i] else "DIFFERENT"
        print(f"{s['id']:<15} | {s['label']:<6} | {s.get('watermark_type','clean'):<16} | {p_prob:11.4f}  | {l_prob:11.4f}  | {match_str}")
    print("=" * 90)

    # Group by category for Logistic Regression
    eval_records = []
    for s, prob, pred in zip(test_samples, logreg_probs, logreg_preds):
        eval_records.append({
            "id": s["id"],
            "text": s["text"],
            "label": s["label"],
            "watermark_type": s.get("watermark_type", "clean"),
            "prob": prob,
            "pred": pred
        })

    from collections import defaultdict
    by_category = defaultdict(list)
    for r in eval_records:
        by_category[r["watermark_type"]].append(r)

    print("\n" + "=" * 115)
    print("PURE LOGISTIC REGRESSION BASELINE EVALUATION (UNBIASED, NO HEURISTICS, N=750)")
    print("=" * 115)
    print(f"{'Category':<18} | {'Raw Counts':<12} | {'Recall [95% CI]':<25} | {'Precision [95% CI]':<25} | {'F1-Score'}")
    print("-" * 115)

    for cat, recs in sorted(by_category.items()):
        n_tot = len(recs)
        if cat == "clean":
            spec_point, spec_low, spec_high = bootstrap_ci(
                lambda data: sum(1 for d in data if d["pred"] == 0) / max(1, len(data)), recs
            )
            tn_cnt = sum(1 for d in recs if d["pred"] == 0)
            raw_str = f"{tn_cnt}/{n_tot}"
            spec_str = f"{spec_point*100:5.1f}% [{spec_low*100:5.1f}% - {spec_high*100:5.1f}%]"
            print(f"{cat:<18} | {raw_str:<12} | Spec: {spec_str:<25} | {'N/A':<25} | {'N/A'}")
        else:
            rec_point, rec_low, rec_high = bootstrap_ci(
                lambda data: sum(1 for d in data if d["pred"] == 1) / max(1, len(data)), recs
            )
            prec_point, prec_low, prec_high = bootstrap_ci(
                lambda data: sum(1 for d in data if d["pred"] == 1) / max(1, sum(1 for d in data if d["pred"] == 1)), recs
            )
            tp_cnt = sum(1 for d in recs if d["pred"] == 1)
            raw_str = f"{tp_cnt}/{n_tot}"
            rec_str = f"{rec_point*100:5.1f}% [{rec_low*100:5.1f}% - {rec_high*100:5.1f}%]"
            prec_str = f"{prec_point*100:5.1f}% [{prec_low*100:5.1f}% - {prec_high*100:5.1f}%]"
            f1 = 2 * prec_point * rec_point / max(1e-6, (prec_point + rec_point))
            print(f"{cat:<18} | {raw_str:<12} | {rec_str:<25} | {prec_str:<25} | {f1:.3f}")

    print("=" * 115 + "\n")

if __name__ == "__main__":
    run_logistic_regression_baseline()
