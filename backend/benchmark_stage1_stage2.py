"""
Benchmark Script for Stage 1 (Physical Scanner) & Stage 2 (KGW Statistical Test)
Evaluates precision, recall, and 95% bootstrapped confidence intervals in isolation on test_data_heldout.json
"""
import os
import re
import json
import numpy as np
from typing import Dict, Tuple, Set

# ==============================================================================
# STAGE 1: Deterministic Physical Scanner
# ==============================================================================
INVISIBLE_PATTERN = re.compile(
    r'[\u200B\u200C\u200D\uFEFF\u200E\u200F\u2060\u2061-\u2064\uFE00-\uFE0F\u00AD\U000E0020-\U000E007F]'
)

def load_confusables(path: str = "backend/data/confusables_sept2022.json") -> Dict[str, str]:
    """Builds reverse map from confusable char -> target ASCII char"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    reverse_map = {}
    for target_char, confusables in data.items():
        # We only care about standard ASCII / Latin targets
        if len(target_char) == 1 and ord(target_char) < 128:
            for conf in confusables:
                if len(conf) == 1 and ord(conf) >= 128:
                    reverse_map[conf] = target_char
    # Also ensure standard cyrillic lookalikes are included
    cyrillic_map = {'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'у': 'y', 'х': 'x',
                    'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M', 'Н': 'N', 'О': 'O',
                    'Р': 'P', 'С': 'C', 'Т': 'T', 'Х': 'X'}
    reverse_map.update(cyrillic_map)
    return reverse_map

CONFUSABLE_MAP = load_confusables()

def stage1_scan_physical(text: str) -> Dict[str, bool]:
    """
    Stage 1: Deterministic Physical Scanner (<0.1ms)
    Detects zero-width steganography and homoglyph substitutions.
    """
    stego_matches = INVISIBLE_PATTERN.findall(text)
    has_stego = len(stego_matches) > 0
    
    has_homoglyph = any(c in CONFUSABLE_MAP for c in text)
    
    return {
        "stego": has_stego,
        "homoglyph": has_homoglyph
    }

# ==============================================================================
# STAGE 2: Closed-Form Statistical Test for KGW (Synonym Map Match)
# ==============================================================================
from ml_dataset_generator import GREEN_LIST_MAP

# Build specific green synonym list (excluding common English stop words or unigram fragments of phrases)
STOP_WORDS = {"for", "in", "the", "a", "an", "and", "or", "of", "to", "with"}
BASE_CORPUS_WORDS = {"data", "systems", "architectures"}

# Dictionary of specific replacement phrases/words
EXACT_GREEN_PHRASES = []
EXACT_GREEN_WORDS = set()

for base_word, syns in GREEN_LIST_MAP.items():
    for syn in syns:
        clean_syn = syn.lower().strip()
        if " " in clean_syn:
            EXACT_GREEN_PHRASES.append(clean_syn)
        else:
            w = re.sub(r'[^\w]', '', clean_syn)
            if w and w not in STOP_WORDS and w not in BASE_CORPUS_WORDS:
                EXACT_GREEN_WORDS.add(w)

def stage2_kgw_statistical_test(text: str, z_threshold: float = 2.0, min_hits: int = 1) -> Dict:
    """
    Stage 2: Closed-Form Statistical Test for KGW (<0.5ms)
    Matches directly against GREEN_LIST_MAP's green-side vocabulary.
    Computes binomial Z-score against expected baseline rate.
    """
    lower_text = text.lower()
    words = text.split()
    clean_words = [re.sub(r'[^\w]', '', w).lower() for w in words if w]
    n_words = max(1, len(clean_words))
    
    matched_items = []
    
    # Check multi-word phrase matches
    for phrase in EXACT_GREEN_PHRASES:
        if phrase in lower_text:
            matched_items.append(phrase)
            
    # Check single-word synonym matches
    for w in clean_words:
        if w in EXACT_GREEN_WORDS:
            matched_items.append(w)
            
    k_green = len(matched_items)
    
    # Expected baseline rate on clean text for these specific rare synonyms
    p_0 = 0.003
    expected_mean = n_words * p_0
    expected_std = max(1e-6, (n_words * p_0 * (1.0 - p_0)) ** 0.5)
    
    z_score = (k_green - expected_mean) / expected_std
    
    is_flagged = (z_score >= z_threshold) and (k_green >= min_hits)
    
    return {
        "kgw_zscore": round(float(z_score), 4),
        "kgw_matches": k_green,
        "total_words": n_words,
        "kgw_flagged": bool(is_flagged),
        "matched_words": matched_items
    }

# ==============================================================================
# Evaluation Harness with Bootstrapping
# ==============================================================================
def bootstrap_metric(y_true, y_pred, metric_func, n_bootstraps=1000, alpha=0.05):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    n = len(y_true)
    if n == 0:
        return 0.0, 0.0, 0.0
    
    np.random.seed(42)
    boot_stats = []
    for _ in range(n_bootstraps):
        idx = np.random.randint(0, n, size=n)
        boot_stats.append(metric_func(y_true[idx], y_pred[idx]))
    
    val = metric_func(y_true, y_pred)
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

def run_isolated_benchmark():
    test_path = "backend/data/test_data_heldout.json"
    with open(test_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
    
    print(f"\n{'='*100}")
    print(f"BENCHMARK: STAGE 1 & STAGE 2 IN ISOLATION (N={len(samples)} on {test_path})")
    print(f"{'='*100}")
    
    # Ground truth splits
    stego_samples = [s for s in samples if s.get("watermark_type") in ("steganography", "hybrid")]
    kgw_samples = [s for s in samples if s.get("watermark_type") == "kgw_token_bias"]
    clean_samples = [s for s in samples if s.get("watermark_type") == "clean"]
    synthid_samples = [s for s in samples if s.get("watermark_type") == "synthid_ngram"]
    
    # 1. Evaluate Stage 1 (Stego & Homoglyphs)
    print("\n--- STAGE 1: PHYSICAL SCANNER (Stego / Homoglyphs) ---")
    stego_preds = [1 if (stage1_scan_physical(s["text"])["stego"] or stage1_scan_physical(s["text"])["homoglyph"]) else 0 for s in samples]
    stego_trues = [1 if s.get("watermark_type") in ("steganography", "hybrid") else 0 for s in samples]
    
    rec, r_lo, r_hi = bootstrap_metric(stego_trues, stego_preds, recall_fn)
    prec, p_lo, p_hi = bootstrap_metric(stego_trues, stego_preds, precision_fn)
    print(f"Stego/Hybrid Recall:    {rec*100:.1f}% [{r_lo*100:.1f}% - {r_hi*100:.1f}%] (Raw: {sum(stego_preds[i] for i in range(len(samples)) if stego_trues[i]==1)}/{len(stego_samples)})")
    print(f"Stego/Hybrid Precision: {prec*100:.1f}% [{p_lo*100:.1f}% - {p_hi*100:.1f}%]")
    
    # Clean specificity for Stage 1 alone
    clean_stego_preds = [stego_preds[i] for i in range(len(samples)) if samples[i].get("watermark_type") == "clean"]
    clean_stego_trues = [0] * len(clean_samples)
    spec, s_lo, s_hi = bootstrap_metric(clean_stego_trues, clean_stego_preds, spec_fn)
    print(f"Clean Specificity:      {spec*100:.1f}% [{s_lo*100:.1f}% - {s_hi*100:.1f}%] (False Positives: {sum(clean_stego_preds)}/{len(clean_samples)})")
    
    # 2. Evaluate Stage 2 (KGW Statistical Test) across various Z-thresholds
    print("\n--- STAGE 2: KGW STATISTICAL TEST (Synonym Map Match) ---")
    print(f"{'Z-Thresh':<10} | {'KGW Recall [95% CI]':<30} | {'Clean Specificity [95% CI]':<30} | {'KGW Prec':<10}")
    print("-" * 90)
    
    kgw_trues = [1 if s.get("watermark_type") == "kgw_token_bias" else 0 for s in samples]
    
    for z_t in [1.0, 1.5, 1.8, 2.0, 2.2, 2.5]:
        kgw_preds = [1 if stage2_kgw_statistical_test(s["text"], z_threshold=z_t, min_hits=1)["kgw_flagged"] else 0 for s in samples]
        
        rec, r_lo, r_hi = bootstrap_metric(kgw_trues, kgw_preds, recall_fn)
        prec, p_lo, p_hi = bootstrap_metric(kgw_trues, kgw_preds, precision_fn)
        
        clean_kgw_preds = [kgw_preds[i] for i in range(len(samples)) if samples[i].get("watermark_type") == "clean"]
        clean_kgw_trues = [0] * len(clean_samples)
        spec, s_lo, s_hi = bootstrap_metric(clean_kgw_trues, clean_kgw_preds, spec_fn)
        
        raw_hits = sum(kgw_preds[i] for i in range(len(samples)) if kgw_trues[i]==1)
        raw_fps = sum(clean_kgw_preds)
        print(f"Z >= {z_t:<5.1f} | {rec*100:5.1f}% [{r_lo*100:5.1f}% - {r_hi*100:5.1f}%] ({raw_hits:2d}/{len(kgw_samples)}) | {spec*100:5.1f}% [{s_lo*100:5.1f}% - {s_hi*100:5.1f}%] (FP: {raw_fps:2d}) | {prec*100:5.1f}%")

if __name__ == "__main__":
    run_isolated_benchmark()
