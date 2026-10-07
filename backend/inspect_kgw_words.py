"""
Analyze clean false positives in Stage 2 KGW matching
"""
import re
import json
from benchmark_stage1_stage2 import ALL_GREEN_SYNONYMS, stage2_kgw_statistical_test
from collections import Counter

with open("backend/data/test_data_heldout.json", "r", encoding="utf-8") as f:
    samples = json.load(f)

clean_samples = [s for s in samples if s.get("watermark_type") == "clean"]
kgw_samples = [s for s in samples if s.get("watermark_type") == "kgw_token_bias"]

clean_fp_words = Counter()
for s in clean_samples:
    res = stage2_kgw_statistical_test(s["text"], z_threshold=2.0)
    if res["kgw_flagged"]:
        for w in res["matched_words"]:
            clean_fp_words[w] += 1

print("Most frequent green words in clean text (causing FPs):")
for w, c in clean_fp_words.most_common(15):
    print(f"  {w}: {c}")

kgw_hit_words = Counter()
for s in kgw_samples:
    res = stage2_kgw_statistical_test(s["text"], z_threshold=2.0)
    for w in res["matched_words"]:
        kgw_hit_words[w] += 1

print("\nMost frequent green words in KGW text:")
for w, c in kgw_hit_words.most_common(15):
    print(f"  {w}: {c}")
