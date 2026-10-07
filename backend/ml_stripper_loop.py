"""
ml_stripper_loop.py — Detector-Guided Iterative Text Stripping & Gated Feedback Logging

Integrates with StagedWatermarkPipeline:
- Stage 5 targeted physical and lexical stripping.
- Feedback logging is strictly GATED:
  * Excludes ambiguous confidence (0.05 < P < 0.95) from the feedback buffer.
  * Only logs verified high-certainty pairs to prevent Model Autophagy / feedback poisoning.
"""
import os
import json
import time
from typing import Dict, Tuple, Optional
from staged_watermark_pipeline import StagedWatermarkPipeline

FEEDBACK_LOG_PATH = "backend/data/feedback_dataset.jsonl"

class MLGuidedStripperLoop:
    """
    Orchestrates staged targeted stripping and gated feedback logging.
    """
    def __init__(self):
        self.pipeline = StagedWatermarkPipeline()

    def log_feedback_pair(self, original_text: str, cleaned_text: str, detection_struct: Dict, is_effective: bool):
        """
        Appends (original_text, cleaned_text) pair to feedback log ONLY if confidence is unambiguous.
        Safeguard: Excludes ambiguous samples (0.05 < P < 0.95) to protect future training data integrity.
        """
        # Gating check: only log if clear physical marker was found or risk was extreme
        has_physical_marker = detection_struct.get("stego", False) or detection_struct.get("homoglyph", False)
        synth_risk = detection_struct.get("synthid_risk", 0.0)
        is_unambiguous = has_physical_marker or (synth_risk >= 0.95) or (synth_risk <= 0.05)
        
        if not is_unambiguous:
            return  # Exclude ambiguous samples from training buffer
            
        try:
            os.makedirs(os.path.dirname(FEEDBACK_LOG_PATH), exist_ok=True)
            log_entry = {
                "timestamp": time.time(),
                "original_text": original_text,
                "cleaned_text": cleaned_text,
                "stego": detection_struct.get("stego", False),
                "homoglyph": detection_struct.get("homoglyph", False),
                "kgw_flagged": detection_struct.get("kgw_flagged", False),
                "synthid_risk": synth_risk,
                "is_effective": is_effective
            }
            with open(FEEDBACK_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[-] Failed to log feedback pair: {e}")

    def process_text_with_feedback(self, text: str) -> Dict:
        """
        Executes 5-stage detection and targeted stripping workflow.
        """
        detection = self.pipeline.detect(text)
        
        if not detection["is_watermarked"]:
            return {
                "original_text": text,
                "stripped_text": text,
                "is_clean": True,
                "detected_types": ["clean"],
                "detection_audit": detection,
                "diff_summary": "Text is already clean. No watermarks detected.",
                "edits_applied": []
            }
            
        strip_result = self.pipeline.stage5_targeted_strip(text, detection_result=detection)
        
        # Verify post-cleaning
        post_detection = self.pipeline.detect(strip_result["cleaned_text"])
        is_effective = not post_detection["is_watermarked"]
        
        # Log gated feedback pair
        self.log_feedback_pair(text, strip_result["cleaned_text"], detection, is_effective)
        
        return {
            "original_text": text,
            "stripped_text": strip_result["cleaned_text"],
            "is_clean": is_effective,
            "detected_types": detection["detected_categories"],
            "detection_audit": detection,
            "post_cleaning_audit": post_detection,
            "diff_summary": strip_result["diff_summary"],
            "edits_applied": strip_result["edits_applied"]
        }

# Global singleton instance
global_ml_stripper = MLGuidedStripperLoop()
