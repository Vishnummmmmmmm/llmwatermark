"""
KGW (Kirchenbauer et al.) Watermark Isolation & Diagnostic Tool
Analyzes token-level green-list hit patterns, run-length burstiness, and 2-word/3-word micro-windows
on 100 KGW watermarked vs 100 clean text samples to diagnose black-box KGW detectability.
"""
import math
import re
from collections import defaultdict
from ml_dataset_generator import WatermarkDatasetGenerator, BASE_CLEAN_CORPUS, GREEN_LIST_MAP

# Green list vocabulary set
GREEN_LIST_VOCAB = {
    "crucial", "essential", "significant", "vital", "produce", "construct", "formulate",
    "synthetic", "man-made", "simulated", "cognition", "intellect", "reasoning", "system",
    "architecture", "framework", "signature", "trace", "marker", "imprint", "identification",
    "discovery", "sensing", "probabilistic", "empirical", "quantitative", "selecting",
    "filtering", "revolutionizing", "reshaping", "modifying", "contemporary", "intricate",
    "expandable", "elastic", "corpora", "guarantee", "assure", "demands", "necessitates",
    "comprehend", "discern", "safeguard", "shield", "swiftly", "hinge", "orchestrate"
}

def analyze_token_hits(text: str) -> dict:
    """
    Extracts token-level green-list hit patterns, run lengths, bi-gram transitions,
    and 2-word / 3-word micro-window densities.
    """
    words = text.split()
    clean_words = [re.sub(r'[^\w]', '', w).lower() for w in words if w]
    total_words = max(1, len(clean_words))

    # Binary hit sequence: 1 if word in green-list vocab, 0 otherwise
    hits = [1 if w in GREEN_LIST_VOCAB else 0 for w in clean_words]
    total_hits = sum(hits)
    global_ratio = total_hits / total_words

    # Run-length burstiness (max consecutive green-list hits)
    max_run_length = 0
    current_run = 0
    for h in hits:
        if h == 1:
            current_run += 1
            max_run_length = max(max_run_length, current_run)
        else:
            current_run = 0

    # 1->1 Bi-gram transition count
    bigram_hits = sum(1 for i in range(len(hits) - 1) if hits[i] == 1 and hits[i + 1] == 1)

    # 2-word micro-window max green ratio
    win2_ratios = [sum(hits[i:i+2])/2.0 for i in range(len(hits)-1)] if len(hits) >= 2 else [global_ratio]
    max_win2 = max(win2_ratios)

    # 3-word micro-window max green ratio
    win3_ratios = [sum(hits[i:i+3])/3.0 for i in range(len(hits)-2)] if len(hits) >= 3 else [global_ratio]
    max_win3 = max(win3_ratios)

    return {
        "total_words": total_words,
        "total_hits": total_hits,
        "global_ratio": round(global_ratio, 4),
        "max_run_length": max_run_length,
        "bigram_hits": bigram_hits,
        "max_win2": round(max_win2, 4),
        "max_win3": round(max_win3, 4)
    }

def run_kgw_diagnostic(num_samples: int = 100):
    """
    Generates 100 KGW watermarked samples (with bias=0.55) vs 100 clean samples
    and compares signal distributions.
    """
    gen = WatermarkDatasetGenerator()
    
    clean_metrics = []
    kgw_metrics = []

    for i in range(num_samples):
        # Pick base text
        base_text = gen.generate_dataset(2)[0]["original_text"]
        
        # Clean sample
        c_m = analyze_token_hits(base_text)
        clean_metrics.append(c_m)

        # KGW watermarked sample (bias = 0.55)
        kgw_text = gen.apply_kgw_watermark(base_text, bias_ratio=0.55)
        k_m = analyze_token_hits(kgw_text)
        kgw_metrics.append(k_m)

    # Aggregate stats
    avg_c_ratio = sum(m["global_ratio"] for m in clean_metrics) / num_samples
    avg_k_ratio = sum(m["global_ratio"] for m in kgw_metrics) / num_samples

    avg_c_win2 = sum(m["max_win2"] for m in clean_metrics) / num_samples
    avg_k_win2 = sum(m["max_win2"] for m in kgw_metrics) / num_samples

    avg_c_win3 = sum(m["max_win3"] for m in clean_metrics) / num_samples
    avg_k_win3 = sum(m["max_win3"] for m in kgw_metrics) / num_samples

    avg_c_run = sum(m["max_run_length"] for m in clean_metrics) / num_samples
    avg_k_run = sum(m["max_run_length"] for m in kgw_metrics) / num_samples

    print("\n" + "=" * 85)
    print(f"KGW WATERMARK ISOLATION DIAGNOSTIC REPORT (N={num_samples} Clean vs N={num_samples} KGW)")
    print("=" * 85)
    print(f"{'Feature Metric':<32} | {'Clean Text Avg':<16} | {'KGW Watermark Avg':<18} | {'Signal Delta'}")
    print("-" * 85)
    print(f"{'Global Green-List Ratio':<32} | {avg_c_ratio:<16.4f} | {avg_k_ratio:<18.4f} | +{(avg_k_ratio-avg_c_ratio)*100:.2f}%")
    print(f"{'2-Word Window Max Density (Win2)':<32} | {avg_c_win2:<16.4f} | {avg_k_win2:<18.4f} | +{(avg_k_win2-avg_c_win2)*100:.2f}%")
    print(f"{'3-Word Window Max Density (Win3)':<32} | {avg_c_win3:<16.4f} | {avg_k_win3:<18.4f} | +{(avg_k_win3-avg_c_win3)*100:.2f}%")
    print(f"{'Max Consecutive Run Length':<32} | {avg_c_run:<16.2f} | {avg_k_run:<18.2f} | +{avg_k_run-avg_c_run:.2f} words")
    print("=" * 85)

    # Test threshold-based separation with 2-word micro-window + run length
    # Threshold rule: max_win2 >= 0.5 or max_run_length >= 2 or global_ratio > 0.18
    detected_clean = sum(1 for m in clean_metrics if m["max_win2"] >= 0.50 or m["max_run_length"] >= 2 or m["global_ratio"] > 0.18)
    detected_kgw = sum(1 for m in kgw_metrics if m["max_win2"] >= 0.50 or m["max_run_length"] >= 2 or m["global_ratio"] > 0.18)

    clean_fp = detected_clean / num_samples
    kgw_tpr = detected_kgw / num_samples

    print("\n[DIAGNOSTIC THRESHOLD SEPARATION TEST]")
    print(f"Rule: (Max Win2 >= 0.50) OR (Consecutive Run >= 2) OR (Global Ratio > 0.18)")
    print(f"  - KGW Recall (TPR @ N=100):  {kgw_tpr*100:.1f}% ({detected_kgw}/{num_samples})")
    print(f"  - Clean False Positive Rate: {clean_fp*100:.1f}% ({detected_clean}/{num_samples})")
    print("=" * 85 + "\n")

if __name__ == "__main__":
    run_kgw_diagnostic(num_samples=100)
