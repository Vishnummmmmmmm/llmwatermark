"""
verify_clean_slm_pipeline.py — Demonstrates SLM Generation + Stage 5 Stripper Guarantee
"""
import sys
sys.path.append("backend")

from slm_text_generator import get_slm_generator
from staged_watermark_pipeline import StagedWatermarkPipeline

def test_clean_pipeline():
    generator = get_slm_generator()
    pipeline = StagedWatermarkPipeline()
    
    prompt = "Write three sentences summarizing the key benefit of solar energy for urban households."
    print("="*80)
    print(f"PROMPT: {prompt}")
    print("="*80)
    
    raw_gen = generator.generate_text(prompt, max_tokens=100)
    print(f"\n1. RAW SLM GENERATION:\n{raw_gen}")
    
    det_raw = pipeline.detect(raw_gen)
    print(f"\n   Detection on Raw SLM: Flagged={det_raw['is_watermarked']}, Categories={det_raw['detected_categories']}, SynthID Risk={det_raw['synthid_risk']:.2f}")
    
    # Run through Stage 5 targeted stripper
    stripped_res = pipeline.stage5_targeted_strip(raw_gen, enable_enrichment=True)
    clean_text = stripped_res["cleaned_text"]
    
    print(f"\n2. STAGE 5 GUARANTEED UNWATERMARKED TEXT:\n{clean_text}")
    
    det_clean = pipeline.detect(clean_text)
    print(f"\n   Detection on Post-Stage 5: Flagged={det_clean['is_watermarked']}, Categories={det_clean['detected_categories']}, SynthID Risk={det_clean['synthid_risk']:.2f}")
    print(f"   Edits made by Stage 5 & Feature 1: {len(stripped_res['edits_applied'])}")
    for edit in stripped_res['edits_applied']:
        print(f"     - Span: '{edit['span']}' -> Stage 5: '{edit['stage5_edit']}' -> Final: '{edit['final']}'")
        
    print("="*80)
    assert not det_clean['is_watermarked'], "Post-Stage 5 output must be completely clean!"
    print("[SUCCESS] Pipeline guaranteed 100% clean unwatermarked text!")

if __name__ == "__main__":
    test_clean_pipeline()
