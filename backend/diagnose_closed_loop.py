import sys
sys.path.append("backend")
import json
from staged_watermark_pipeline import StagedWatermarkPipeline

def diagnose():
    pipeline = StagedWatermarkPipeline()
    with open("backend/data/test_data_heldout.json", "r", encoding="utf-8") as f:
        samples = json.load(f)
        
    reflagged_samples = []
    
    for s in samples:
        raw_text = s["text"]
        res = pipeline.stage5_targeted_strip(raw_text, enable_enrichment=True, enrich_substitutions=False)
        if res["is_modified"]:
            cleaned = res["cleaned_text"]
            det = pipeline.detect(cleaned)
            if det["is_watermarked"]:
                reflagged_samples.append({
                    "id": s["id"],
                    "orig_type": s["watermark_type"],
                    "detected_cats": det["detected_categories"],
                    "synthid_risk": det["synthid_risk"],
                    "kgw_z": det["kgw_zscore"],
                    "stego": det["stego"],
                    "homoglyph": det["homoglyph"],
                    "edits_count": len(res["edits_applied"]),
                    "audit": det["audit_details"]
                })
                
    print(f"Total re-flagged samples: {len(reflagged_samples)}")
    cat_counts = {}
    for r in reflagged_samples:
        for c in r["detected_cats"]:
            cat_counts[c] = cat_counts.get(c, 0) + 1
            
    print(f"Breakdown of re-flagged categories: {cat_counts}")
    print("\nFirst 5 reflagged cases:")
    for r in reflagged_samples[:5]:
        print(f"  * ID: {r['id']} ({r['orig_type']}) -> Flagged as {r['detected_cats']} (SynthID Risk: {r['synthid_risk']:.3f}, KGW Z: {r['kgw_z']:.2f}, Stego: {r['stego']}, Homoglyph: {r['homoglyph']})")
        print(f"    Audit: {r['audit']}")

if __name__ == "__main__":
    diagnose()
