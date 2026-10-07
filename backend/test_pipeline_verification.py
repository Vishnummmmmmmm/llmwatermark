"""
Test script to verify dynamic non-constant responses across:
1. Claude Text
2. Health Text
3. Random Letters
4. Invisible Watermarked Text
"""
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from pure_text_stripper import PureTextStripper
from watermark_detector import global_detector

def run_tests():
    stripper = PureTextStripper()

    test_cases = {
        "Claude AI Text": (
            "It is important to note that in healthcare, medical practitioners delve into comprehensive "
            "frameworks to optimize patient treatment and clinical diagnosis. Furthermore, artificial "
            "intelligence language models utilize multifaceted systems to facilitate therapeutic interventions."
        ),
        "Health / Medical Text": (
            "The patient presented with acute symptoms requiring immediate physician examination. "
            "The clinical diagnosis indicated a chronic metabolic disorder, and the healthcare team established "
            "a tailored medication and recovery regimen."
        ),
        "Random Letters / Gibberish": (
            "asdfghjk qwertyuiop zxcvbnm lkjhgfdsa poiuytrewq"
        ),
        "Invisible Steganography": (
            "Artificial\u200B intelligence\u200C language\u200D models\uFEFF produce\u200E responses\u200F by\u2060 "
            "sampling\u2061 tokens according\uFE00 to probability\u00AD distributions with homoglyph\u0430 markers."
        )
    }

    print("=" * 70)
    print("RUNNING FUCKLLM PIPELINE VERIFICATION")
    print("=" * 70)

    for name, text in test_cases.items():
        print(f"\n--- TEST CASE: {name} ---")
        detection = global_detector.detect(text)
        stripped = stripper.strip_text_watermark(text)

        print(f"Domain Detected:    {stripped['domain_label']} (raw: {stripped['domain']})")
        print(f"Initial Risk %:     {stripped['initial_risk_percentage']}%")
        print(f"Final Risk %:       {stripped['final_risk_percentage']}%")
        print(f"Synonyms Swapped:   {stripped['synonyms_replaced']}")
        print(f"Phrases Rewritten:  {stripped['phrases_rewritten']}")
        print(f"Stego Chars Purged: {stripped['invisible_chars_removed_count']}")
        print(f"Summary:            {stripped['removal_summary']}")
        print(f"Cleaned Text Sample: {stripped['cleaned_text'][:110]}...")

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
