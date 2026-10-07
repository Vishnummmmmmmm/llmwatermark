import sys
sys.path.append("backend")
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from staged_watermark_pipeline import StagedWatermarkPipeline

def main():
    pipeline = StagedWatermarkPipeline()
    with open("backend/data/test_data_heldout.json", "r", encoding="utf-8") as f:
        samples = json.load(f)
        
    print("="*90)
    print("ISSUE 1: MULTI-HOP AUDIT TRAIL VERIFICATION (5 CONCRETE EXAMPLES)")
    print("="*90)
    
    test_sample_ids = ["sample_wm_739", "sample_wm_976", "sample_wm_2144", "sample_wm_361", "sample_wm_1763"]
    selected = [s for s in samples if s.get("id") in test_sample_ids]
    
    for s in selected:
        sid = s["id"]
        stype = s["watermark_type"]
        raw_text = s["text"]
        res = pipeline.stage5_targeted_strip(raw_text, enable_enrichment=True, enrich_substitutions=True)
        print(f"\n[SAMPLE {sid}] Category: {stype}")
        for e in res["edits_applied"]:
            span = e.get("span")
            s5 = e.get("stage5_edit")
            f1 = e.get("feature1_edit")
            fin = e.get("final")
            stages = " -> ".join(e.get("stages_applied", []))
            print(f"  * Span: '{span}' | Stage 5: '{s5}' | Feature 1: '{f1}' | Final: '{fin}' [{stages}]")
            
    print("\n" + "="*90)
    print("ISSUE 2: COSINE SIMILARITY SPLIT BY EDIT TYPE (N=750)")
    print("="*90)
    
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), analyzer="word")
    sims_mode_a = []
    sims_mode_b = []
    removal_only_sims = []
    paraphrase_sims = []
    
    for s in samples:
        raw_text = s["text"]
        strip_ref = pipeline.stage5_targeted_strip(raw_text, enable_enrichment=False)["cleaned_text"]
        res_a = pipeline.stage5_targeted_strip(raw_text, enable_enrichment=True, enrich_substitutions=False)
        res_b = pipeline.stage5_targeted_strip(raw_text, enable_enrichment=True, enrich_substitutions=True)
        
        corpus_a = [strip_ref, res_a["cleaned_text"]]
        sim_a = float(cosine_similarity(vectorizer.fit_transform(corpus_a))[0][1])
        sims_mode_a.append(sim_a)
        
        corpus_b = [strip_ref, res_b["cleaned_text"]]
        sim_b = float(cosine_similarity(vectorizer.fit_transform(corpus_b))[0][1])
        sims_mode_b.append(sim_b)
        
        if any(e.get("type") == "synthid_ngram" and e.get("feature1_edit") is not None for e in res_a["edits_applied"]):
            removal_only_sims.append(sim_a)
        if any(e.get("type") == "kgw_token_bias" and e.get("feature1_edit") is not None for e in res_b["edits_applied"]):
            paraphrase_sims.append(sim_b)
            
    a = np.array(sims_mode_a)
    b = np.array(sims_mode_b)
    rem = np.array(removal_only_sims)
    para = np.array(paraphrase_sims)
    
    print(f"\n1. MODE A (Removal-Only Re-Insertion, Production Default):")
    print(f"   Full Held-Out (N=750): Min={a.min():.4f}, Mean={a.mean():.4f}, Median={np.median(a):.4f}, Max={a.max():.4f}, Std={a.std():.4f}")
    print(f"   SynthID Removal Slots Subset (N={len(rem)}): Min={rem.min():.4f}, Mean={rem.mean():.4f}, Median={np.median(rem):.4f}, Max={rem.max():.4f}, Std={rem.std():.4f}")
    
    print(f"\n2. MODE B (Extended Lexical Paraphrasing):")
    print(f"   Full Held-Out (N=750): Min={b.min():.4f}, Mean={b.mean():.4f}, Median={np.median(b):.4f}, Max={b.max():.4f}, Std={b.std():.4f}")
    print(f"   Re-Paraphrased Substitution Slots Subset (N={len(para)}): Min={para.min():.4f}, Mean={para.mean():.4f}, Median={np.median(para):.4f}, Max={para.max():.4f}, Std={para.std():.4f}")

    print("\n" + "="*90)
    print("ISSUE 3: CLOSED-LOOP DETECTION ON ENRICHED OUTPUTS")
    print("="*90)
    
    total_mod = 0
    reflagged_a = 0
    reflagged_b = 0
    
    for s in samples:
        raw_text = s["text"]
        res_a = pipeline.stage5_targeted_strip(raw_text, enable_enrichment=True, enrich_substitutions=False)
        if res_a["is_modified"]:
            total_mod += 1
            det_a = pipeline.detect(res_a["cleaned_text"])
            if det_a["is_watermarked"]:
                reflagged_a += 1
                
        res_b = pipeline.stage5_targeted_strip(raw_text, enable_enrichment=True, enrich_substitutions=True)
        if res_b["is_modified"]:
            det_b = pipeline.detect(res_b["cleaned_text"])
            if det_b["is_watermarked"]:
                reflagged_b += 1
                
    print(f"Total Modified Watermarked Samples Tested: {total_mod}")
    print(f"Closed-Loop Re-Flagged Count (Mode A - Production Default): {reflagged_a} / {total_mod} ({reflagged_a/total_mod*100:.2f}%)")
    print(f"Closed-Loop Re-Flagged Count (Mode B - Extended Paraphrase): {reflagged_b} / {total_mod} ({reflagged_b/total_mod*100:.2f}%)")
    if reflagged_a == 0:
        print(">> PASSED: Exactly 0/{0} samples re-flagged post-enrichment.".format(total_mod))

if __name__ == "__main__":
    main()
