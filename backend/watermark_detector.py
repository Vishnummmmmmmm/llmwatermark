"""
watermark_detector.py — Watermark Detector Interface

Uses FeatureMLPClassifier and StagedWatermarkPipeline to perform:
- Stage 1: Deterministic Physical Scanner (<0.1ms, zero-width + homoglyphs)
- Stage 2: Closed-Form Statistical Test for KGW (<0.5ms, direct synonym match + binomial Z-score)
- Stage 3: FeatureMLPClassifier for SynthID (<1ms, narrowed n-gram features)
- Stage 4: Structured Detection Output
- Stage 5: Targeted Editing / Stripping
"""
import os
import torch
from typing import Dict, Any, Optional
from staged_watermark_pipeline import StagedWatermarkPipeline, FeatureMLPClassifier

class WatermarkDetectorPipeline:
    """
    Unified Watermark Detector Pipeline interface.
    """
    def __init__(self, checkpoint_path: Optional[str] = None):
        self.pipeline = StagedWatermarkPipeline(model_weights_path=checkpoint_path)
        self.checkpoint_path = checkpoint_path or "backend/models/synthid_feature_mlp.pt"
        self.is_trained = self.pipeline.is_model_loaded

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Runs staged detection and returns structured audit output with risk score.
        """
        structured_out = self.pipeline.detect(text)
        
        # Calculate an overall risk percentage for UI display
        if structured_out["stego"] or structured_out["homoglyph"]:
            risk_pct = 98.0
        elif structured_out["synthid_flagged"]:
            risk_pct = round(structured_out["synthid_risk"] * 100.0, 1)
        elif structured_out["kgw_flagged"]:
            risk_pct = min(95.0, round(50.0 + structured_out["kgw_zscore"] * 15.0, 1))
        else:
            risk_pct = 5.0
            
        return {
            "is_watermarked": structured_out["is_watermarked"],
            "risk_percentage": risk_pct,
            "confidence_score": round(risk_pct / 100.0, 4),
            "detected_types": structured_out["detected_categories"],
            "stego": structured_out["stego"],
            "homoglyph": structured_out["homoglyph"],
            "kgw_zscore": structured_out["kgw_zscore"],
            "kgw_flagged": structured_out["kgw_flagged"],
            "synthid_risk": structured_out["synthid_risk"],
            "synthid_flagged": structured_out["synthid_flagged"],
            "is_model_trained": self.is_trained,
            "metrics": {
                "invisible_char_count": structured_out["audit_details"]["invisible_char_count"],
                "homoglyph_count": structured_out["audit_details"]["homoglyph_count"],
                "kgw_green_matches": structured_out["audit_details"]["kgw_green_matches"],
                "synthid_markers_found": structured_out["audit_details"]["synthid_markers_found"]
            }
        }

    def strip(self, text: str) -> Dict[str, Any]:
        """
        Executes Stage 5 targeted stripping and editing.
        """
        det = self.pipeline.detect(text)
        return self.pipeline.stage5_targeted_strip(text, detection_result=det)

# Global singleton instance
global_detector = WatermarkDetectorPipeline()
