"""
Threshold Calibration & ROC Curve Analysis (DEV SET ONLY)
Evaluates decision thresholds T from 0.50 to 0.90 in steps of 0.05 on backend/data/dev_data.json.
Selects optimal threshold T that maintains Clean Specificity >= 90% while maximizing recall.
"""
import re
import json
import torch
import numpy as np
from watermark_detector import WatermarkDetectorPipeline
from eval_bootstrap import bootstrap_ci

DEV_DATA_PATH = "backend/data/dev_data.json"

def tune_threshold_on_dev_set():
    with open(DEV_DATA_PATH, "r", encoding="utf-8") as f:
        dev_samples = json.load(f)

    pipeline = WatermarkDetectorPipeline()
    model = pipeline.model
    model.eval()

    # Pre-extract probabilities for all dev samples
    records = []
    for s in dev_samples:
        text = s["text"]
        label = s["label"]
        wm_type = s.get("watermark_type", "clean")

        res = pipeline.detect(text)
        prob = res["confidence_score"]

        records.append({
            "id": s["id"],
            "label": label,
            "watermark_type": wm_type,
            "prob": prob
        })

    thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]

    print("\n" + "=" * 125)
    print("THRESHOLD CALIBRATION ROC & PRECISION-RECALL CURVE (DEV SET ONLY, N=750)")
    print("=" * 125)
    print(f"{'T':<5} | {'Clean Spec':<12} | {'Stego Rec':<12} | {'Hybrid Rec':<12} | {'SynthID Rec':<12} | {'KGW Rec':<12} | {'Macro F1':<10} | {'Status'}")
    print("-" * 125)

    best_t = 0.50
    best_macro_f1 = 0.0

    for T in thresholds:
        clean_recs = [r for r in records if r["watermark_type"] == "clean"]
        stego_recs = [r for r in records if r["watermark_type"] == "steganography"]
        hyb_recs = [r for r in records if r["watermark_type"] == "hybrid"]
        synth_recs = [r for r in records if r["watermark_type"] == "synthid_ngram"]
        kgw_recs = [r for r in records if r["watermark_type"] == "kgw_token_bias"]

        clean_spec = sum(1 for r in clean_recs if r["prob"] <= T) / max(1, len(clean_recs))
        stego_rec = sum(1 for r in stego_recs if r["prob"] > T) / max(1, len(stego_recs))
        hyb_rec = sum(1 for r in hyb_recs if r["prob"] > T) / max(1, len(hyb_recs))
        synth_rec = sum(1 for r in synth_recs if r["prob"] > T) / max(1, len(synth_recs))
        kgw_rec = sum(1 for r in kgw_recs if r["prob"] > T) / max(1, len(kgw_recs))

        macro_f1 = (clean_spec + stego_rec + hyb_rec + synth_rec + kgw_rec) / 5.0
        status_str = "VALID (Spec >= 90%)" if clean_spec >= 0.90 else "BELOW TARGET"

        if clean_spec >= 0.90 and macro_f1 > best_macro_f1:
            best_macro_f1 = macro_f1
            best_t = T

        print(f"{T:<5.2f} | {clean_spec*100:11.1f}% | {stego_rec*100:11.1f}% | {hyb_rec*100:11.1f}% | {synth_rec*100:11.1f}% | {kgw_rec*100:11.1f}% | {macro_f1:9.3f} | {status_str}")

    print("=" * 125)
    print(f"[+] OPTIMAL LOCKED THRESHOLD ON DEV SET: T = {best_t:.2f} (Clean Spec = {clean_spec*100:.1f}%)\n")
    return best_t

if __name__ == "__main__":
    tune_threshold_on_dev_set()
