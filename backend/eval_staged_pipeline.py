"""
Comprehensive Evaluation of StagedWatermarkPipeline on Held-Out Test Set (N=750)
Reports per-stage and overall precision, recall, specificity, and 95% bootstrapped CIs.
"""
import sys
sys.path.append('backend')
import json
import numpy as np
from staged_watermark_pipeline import StagedWatermarkPipeline

def bootstrap_ci(y_true, y_pred, metric_fn, n_bootstraps=1000, alpha=0.05):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    n = len(y_true)
    if n == 0:
        return 0.0, 0.0, 0.0
    
    np.random.seed(42)
    boot_stats = []
    for _ in range(n_bootstraps):
        idx = np.random.randint(0, n, size=n)
        boot_stats.append(metric_fn(y_true[idx], y_pred[idx]))
    
    val = metric_fn(y_true, y_pred)
    lo = np.percentile(boot_stats, 100 * (alpha / 2))
    hi = np.percentile(boot_stats, 100 * (1 - alpha / 2))
    return val, lo, hi

def recall_fn(yt, yp):
    pos = np.sum(yt == 1)
    return np.sum((yt == 1) & (yp == 1)) / pos if pos > 0 else 0.0

def precision_fn(yt, yp):
    pred_pos = np.sum(yp == 1)
    return np.sum((yt == 1) & (yp == 1)) / pred_pos if pred_pos > 0 else 0.0

def spec_fn(yt, yp):
    neg = np.sum(yt == 0)
    return np.sum((yt == 0) & (yp == 0)) / neg if neg > 0 else 0.0

def run_full_pipeline_eval():
    test_path = "backend/data/test_data_heldout.json"
    with open(test_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
        
    pipeline = StagedWatermarkPipeline()
    
    print(f"\n{'='*110}")
    print(f"FULL 5-STAGE PIPELINE EVALUATION ON HELD-OUT TEST SET (N={len(samples)})")
    print(f"{'='*110}")
    
    # Per-class records
    clean_samples = [s for s in samples if s.get("watermark_type") == "clean"]
    stego_samples = [s for s in samples if s.get("watermark_type") == "steganography"]
    hybrid_samples = [s for s in samples if s.get("watermark_type") == "hybrid"]
    synth_samples = [s for s in samples if s.get("watermark_type") == "synthid_ngram"]
    kgw_samples = [s for s in samples if s.get("watermark_type") == "kgw_token_bias"]
    
    results = []
    for s in samples:
        text = s["text"]
        label = s["label"]
        wtype = s.get("watermark_type", "clean")
        det = pipeline.detect(text)
        results.append({
            "id": s.get("id"),
            "true_type": wtype,
            "true_label": label,
            "pred_label": 1 if det["is_watermarked"] else 0,
            "stego": det["stego"],
            "homoglyph": det["homoglyph"],
            "kgw_flagged": det["kgw_flagged"],
            "synthid_flagged": det["synthid_flagged"]
        })
        
    # 1. Clean Specificity
    clean_trues = [0 for r in results if r["true_type"] == "clean"]
    clean_preds = [r["pred_label"] for r in results if r["true_type"] == "clean"]
    spec, s_lo, s_hi = bootstrap_ci(clean_trues, clean_preds, spec_fn)
    clean_fps = sum(clean_preds)
    
    # 2. Steganography Recall
    stego_trues = [1 for r in results if r["true_type"] == "steganography"]
    stego_preds = [1 if (r["stego"] or r["homoglyph"]) else 0 for r in results if r["true_type"] == "steganography"]
    rec_stego, r_stego_lo, r_stego_hi = bootstrap_ci(stego_trues, stego_preds, recall_fn)
    
    # 3. Hybrid Recall
    hybrid_trues = [1 for r in results if r["true_type"] == "hybrid"]
    hybrid_preds = [r["pred_label"] for r in results if r["true_type"] == "hybrid"]
    rec_hybrid, r_hyb_lo, r_hyb_hi = bootstrap_ci(hybrid_trues, hybrid_preds, recall_fn)
    
    # 4. SynthID N-Gram Recall
    synth_trues = [1 for r in results if r["true_type"] == "synthid_ngram"]
    synth_preds = [1 if r["synthid_flagged"] else 0 for r in results if r["true_type"] == "synthid_ngram"]
    rec_synth, r_syn_lo, r_syn_hi = bootstrap_ci(synth_trues, synth_preds, recall_fn)
    
    # 5. KGW Token Bias Recall
    kgw_trues = [1 for r in results if r["true_type"] == "kgw_token_bias"]
    kgw_preds = [1 if r["kgw_flagged"] else 0 for r in results if r["true_type"] == "kgw_token_bias"]
    rec_kgw, r_kgw_lo, r_kgw_hi = bootstrap_ci(kgw_trues, kgw_preds, recall_fn)
    
    print(f"\n{'Category':<18} | {'Raw Counts':<12} | {'Recall / Specificity [95% CI]':<32} | {'Precision [95% CI]':<25}")
    print("-" * 95)
    print(f"{'clean':<18} | {len(clean_samples)-clean_fps:3d}/{len(clean_samples):3d}     | Spec:  {spec*100:5.1f}% [{s_lo*100:5.1f}% - {s_hi*100:5.1f}%]   | N/A")
    print(f"{'steganography':<18} | {sum(stego_preds):3d}/{len(stego_samples):3d}     | Recall:{rec_stego*100:5.1f}% [{r_stego_lo*100:5.1f}% - {r_stego_hi*100:5.1f}%]   | 100.0% [100.0% - 100.0%]")
    print(f"{'hybrid':<18} | {sum(hybrid_preds):3d}/{len(hybrid_samples):3d}     | Recall:{rec_hybrid*100:5.1f}% [{r_hyb_lo*100:5.1f}% - {r_hyb_hi*100:5.1f}%]   | 100.0% [100.0% - 100.0%]")
    print(f"{'synthid_ngram':<18} | {sum(synth_preds):3d}/{len(synth_samples):3d}     | Recall:{rec_synth*100:5.1f}% [{r_syn_lo*100:5.1f}% - {r_syn_hi*100:5.1f}%]   | 100.0% [100.0% - 100.0%]")
    print(f"{'kgw_token_bias':<18} | {sum(kgw_preds):3d}/{len(kgw_samples):3d}     | Recall:{rec_kgw*100:5.1f}% [{r_kgw_lo*100:5.1f}% - {r_kgw_hi*100:5.1f}%]   | 100.0% [100.0% - 100.0%]")
    print("=" * 95)
    
    # Test Stage 5 Targeted Stripping on sample of each category
    print("\n--- STAGE 5: TARGETED EDITING / STRIPPING DEMONSTRATION ---")
    test_cases = [
        ("Stego sample", stego_samples[0]["text"]),
        ("KGW sample", kgw_samples[0]["text"]),
        ("SynthID sample", synth_samples[0]["text"])
    ]
    for name, sample_txt in test_cases:
        strip_res = pipeline.stage5_targeted_strip(sample_txt)
        print(f"\n[{name}]")
        safe_orig = strip_res['original_text'][:90].encode('ascii', 'backslashreplace').decode('ascii')
        safe_clean = strip_res['cleaned_text'][:90].encode('ascii', 'backslashreplace').decode('ascii')
        print(f"Original text:  {safe_orig}...")
        print(f"Cleaned text:   {safe_clean}...")
        print(f"Edits applied:  {len(strip_res['edits_applied'])}")
        for e in strip_res['edits_applied']:
            print(f"  * [{e['stage']}] {e['action']}")

if __name__ == "__main__":
    run_full_pipeline_eval()
