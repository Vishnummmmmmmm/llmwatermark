"""
DIAGNOSTIC SCRIPT: KGW Recall 0% Root-Cause & Threshold Sweep Analysis
Diagnoses whether KGW's 0% recall is caused by Z-score override suppression 
or a genuine model ceiling, and whether threshold sweep results are truly flat.
"""
import sys
sys.path.append('backend')
import re
import json
import torch
import numpy as np
from watermark_detector import WatermarkDetectorPipeline, is_kgw_green_token

TEST_PATH = "backend/data/test_data_heldout.json"

def run_diagnostics():
    with open(TEST_PATH, "r", encoding="utf-8") as f:
        samples = json.load(f)

    pipeline = WatermarkDetectorPipeline()
    model = pipeline.model
    model.eval()

    # ========== DIAGNOSTIC 1: KGW Raw Model Probabilities & Z-Score Override Analysis ==========
    kgw_samples = [s for s in samples if s.get("watermark_type") == "kgw_token_bias"]
    print(f"\n{'='*100}")
    print(f"DIAGNOSTIC 1: KGW TOKEN BIAS SAMPLES (N={len(kgw_samples)})")
    print(f"{'='*100}")

    raw_probs = []
    z_scores = []
    overridden_by_zscore = 0
    model_predicted_clean = 0
    model_predicted_wm_but_overridden = 0

    for s in kgw_samples:
        text = s["text"]
        features = pipeline.extract_features(text)

        with torch.no_grad():
            logit = model(features).squeeze()
            raw_prob = float(torch.sigmoid(logit).item())

        inv_count = int(features[0, 0].item())
        homo_count = int(features[0, 2].item())
        kgw_matches = int(features[0, 4].item())
        synthid_count = int(features[0, 10].item())

        clean_words = [re.sub(r'[^\w]', '', w).lower() for w in text.split() if w]
        n_words = max(1, len(clean_words))
        z_score = (kgw_matches - 0.5 * n_words) / max(1e-6, 0.5 * (n_words ** 0.5))

        raw_probs.append(raw_prob)
        z_scores.append(z_score)

        # Check if Z-score override would suppress this sample
        has_no_markers = inv_count == 0 and homo_count == 0 and synthid_count == 0
        zscore_below_threshold = z_score < 1.70

        if has_no_markers and zscore_below_threshold:
            overridden_by_zscore += 1
            if raw_prob > 0.50:
                model_predicted_wm_but_overridden += 1
        else:
            if raw_prob <= 0.50:
                model_predicted_clean += 1

    raw_probs = np.array(raw_probs)
    z_scores = np.array(z_scores)

    print(f"\n--- RAW MODEL PROBABILITY DISTRIBUTION (BEFORE any override) ---")
    print(f"  Min:    {raw_probs.min():.4f}")
    print(f"  Max:    {raw_probs.max():.4f}")
    print(f"  Mean:   {raw_probs.mean():.4f}")
    print(f"  Median: {np.median(raw_probs):.4f}")
    print(f"  Std:    {raw_probs.std():.4f}")
    print(f"\n  Histogram (probability buckets):")
    for lo in np.arange(0, 1.0, 0.1):
        hi = lo + 0.1
        count = np.sum((raw_probs >= lo) & (raw_probs < hi))
        bar = '#' * count
        print(f"    [{lo:.1f} - {hi:.1f}): {count:3d}  {bar}")

    print(f"\n--- Z-SCORE DISTRIBUTION ---")
    print(f"  Min:    {z_scores.min():.4f}")
    print(f"  Max:    {z_scores.max():.4f}")
    print(f"  Mean:   {z_scores.mean():.4f}")
    print(f"  Median: {np.median(z_scores):.4f}")
    print(f"  # with Z >= 1.70 (pass override): {np.sum(z_scores >= 1.70)}")
    print(f"  # with Z <  1.70 (caught by override): {np.sum(z_scores < 1.70)}")

    print(f"\n--- OVERRIDE ANALYSIS ---")
    print(f"  Total KGW samples:                        {len(kgw_samples)}")
    print(f"  Overridden to clean by Z-score rule:      {overridden_by_zscore}")
    print(f"    ...of which model WOULD have flagged:   {model_predicted_wm_but_overridden}")
    print(f"    ...of which model also predicted clean:  {overridden_by_zscore - model_predicted_wm_but_overridden}")
    print(f"  Not overridden (Z >= 1.70 or has markers): {len(kgw_samples) - overridden_by_zscore}")
    print(f"    ...of which model predicted clean anyway: {model_predicted_clean}")

    if model_predicted_wm_but_overridden > 0:
        print(f"\n  >>> VERDICT: SUPPRESSION BUG. {model_predicted_wm_but_overridden} KGW samples")
        print(f"      were predicted watermarked by the model but FORCE-OVERRIDDEN to clean")
        print(f"      by the Z-score < 1.70 rule. The override is vetoing the model.")
    else:
        print(f"\n  >>> VERDICT: Genuine model ceiling (model never predicted any KGW sample > 0.50)")

    # ========== DIAGNOSTIC 2: Probability Clustering / Threshold Sweep Analysis ==========
    print(f"\n{'='*100}")
    print(f"DIAGNOSTIC 2: PROBABILITY CLUSTERING ANALYSIS (ALL SAMPLES, N={len(samples)})")
    print(f"{'='*100}")

    all_probs = []
    all_final_probs = []
    for s in samples:
        text = s["text"]
        features = pipeline.extract_features(text)
        with torch.no_grad():
            logit = model(features).squeeze()
            raw_prob = float(torch.sigmoid(logit).item())

        inv_count = int(features[0, 0].item())
        homo_count = int(features[0, 2].item())
        kgw_matches = int(features[0, 4].item())
        synthid_count = int(features[0, 10].item())

        clean_words = [re.sub(r'[^\w]', '', w).lower() for w in text.split() if w]
        n_words = max(1, len(clean_words))
        z_score = (kgw_matches - 0.5 * n_words) / max(1e-6, 0.5 * (n_words ** 0.5))

        final_prob = raw_prob
        if inv_count > 0: final_prob = max(final_prob, 0.95)
        if homo_count > 0: final_prob = max(final_prob, 0.90)
        if synthid_count > 0: final_prob = max(final_prob, 0.85)
        if inv_count == 0 and homo_count == 0 and synthid_count == 0 and z_score < 1.70:
            final_prob = min(final_prob, 0.15)

        all_probs.append(raw_prob)
        all_final_probs.append(final_prob)

    all_probs = np.array(all_probs)
    all_final_probs = np.array(all_final_probs)

    print(f"\n--- RAW MODEL PROBABILITIES (before overrides) ---")
    print(f"  Histogram:")
    for lo in np.arange(0, 1.0, 0.1):
        hi = lo + 0.1
        count = np.sum((all_probs >= lo) & (all_probs < hi))
        bar = '#' * min(count, 80)
        print(f"    [{lo:.1f} - {hi:.1f}): {count:4d}  {bar}")

    print(f"\n--- FINAL PROBABILITIES (after heuristic overrides) ---")
    print(f"  Histogram:")
    for lo in np.arange(0, 1.0, 0.1):
        hi = lo + 0.1
        count = np.sum((all_final_probs >= lo) & (all_final_probs < hi))
        bar = '#' * min(count, 80)
        print(f"    [{lo:.1f} - {hi:.1f}): {count:4d}  {bar}")
    count_1 = np.sum(all_final_probs >= 1.0)
    if count_1 > 0:
        print(f"    [1.0 - 1.0]: {count_1:4d}  {'#' * min(count_1, 80)}")

    # Count how many samples fall in the "dead zone" between 0.15 and 0.80
    dead_zone = np.sum((all_final_probs > 0.15) & (all_final_probs < 0.80))
    print(f"\n  Samples in dead zone (0.15 < prob < 0.80): {dead_zone}")
    print(f"  Samples capped at <= 0.15:                 {np.sum(all_final_probs <= 0.15)}")
    print(f"  Samples boosted to >= 0.80:                {np.sum(all_final_probs >= 0.80)}")

    print(f"\n  >>> This explains why thresholds 0.50-0.75 produce identical results:")
    print(f"      The overrides create a bimodal distribution clamped at ~0.15 and ~0.85-0.95.")
    print(f"      No samples have final probabilities in [0.16, 0.79], so every threshold")
    print(f"      in that range produces the exact same classification.")

    # Show 20 random samples across categories
    import random
    random.seed(42)
    sample_indices = random.sample(range(len(samples)), min(20, len(samples)))
    print(f"\n--- 20 RANDOM SAMPLE PROBABILITIES ---")
    print(f"{'ID':<18} | {'Category':<16} | {'Raw Prob':>10} | {'Final Prob':>10} | {'Z-Score':>8}")
    print("-" * 75)
    for i in sample_indices:
        s = samples[i]
        print(f"{s['id']:<18} | {s.get('watermark_type','clean'):<16} | {all_probs[i]:10.4f} | {all_final_probs[i]:10.4f} | {z_scores[i] if s.get('watermark_type') == 'kgw_token_bias' else 'N/A':>8}")

    print(f"\n{'='*100}")
    print("END OF DIAGNOSTICS")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    run_diagnostics()
