"""
test_slm_generator.py — End-to-End Test for Local SLM Text Generator & Neural Rewriter
"""
import sys
import os
sys.path.append("backend")

from slm_text_generator import get_slm_generator
from staged_watermark_pipeline import StagedWatermarkPipeline

def test_slm():
    print("="*80)
    print("TESTING LOCAL SLM GENERATOR & NEURAL PARAPHRASER (Qwen2.5-0.5B-Instruct)")
    print("="*80)
    
    generator = get_slm_generator()
    detector = StagedWatermarkPipeline()
    
    # --------------------------------------------------------------------------
    # Test 1: Neural Sentence Rewriting
    # --------------------------------------------------------------------------
    sample_watermarked_sentence = "Indeed, it is crucial to note that quantum algorithms guarantee accelerated computation from a structural standpoint."
    print(f"\n[Test 1] Input Watermarked Text:\n  '{sample_watermarked_sentence}'")
    
    det_before = detector.detect(sample_watermarked_sentence)
    print(f"  Watermark Detected Before Rewrite? {det_before['is_watermarked']} (Categories: {det_before['detected_categories']})")
    
    rewritten = generator.rewrite_sentence(sample_watermarked_sentence)
    print(f"\n  SLM Rewritten Text:\n  '{rewritten}'")
    
    det_after = detector.detect(rewritten)
    print(f"  Watermark Detected After Rewrite?  {det_after['is_watermarked']} (Categories: {det_after['detected_categories']})")
    
    # --------------------------------------------------------------------------
    # Test 2: Unwatermarked Text Generation from Prompt
    # --------------------------------------------------------------------------
    prompt = "Explain in two simple sentences why distributed database systems are important for modern cloud applications."
    print(f"\n[Test 2] Prompt Generation:\n  Prompt: '{prompt}'")
    
    generated = generator.generate_text(prompt, max_tokens=80)
    print(f"\n  SLM Generated Output:\n  '{generated}'")
    
    det_gen = detector.detect(generated)
    print(f"\n  Watermark Detected on Generated Output? {det_gen['is_watermarked']} (Categories: {det_gen['detected_categories']})")
    
    print("\n" + "="*80)
    print("SLM GENERATOR TESTS COMPLETED SUCCESSFULLY")
    print("="*80)

if __name__ == "__main__":
    test_slm()
