"""
upload_data_manager.py — Full-Upload Training Data Capture, Consent Gating & Retention Management

Architectural Guarantees:
1. Consent Gate: No data is ever written to disk unless user_consented is explicitly True.
2. Storage vs. Training Separation:
   - Raw Consented Upload Storage: Stores all consented uploads under backend/data/raw_consented_uploads/
   - Training-Eligible Dataset: Only unambiguous samples (P <= 0.05 or P >= 0.95 or physical markers) are added to backend/data/feedback_dataset.jsonl.
     Ambiguous samples (0.05 < P < 0.95) are excluded from training data to prevent Model Autophagy.
3. Retention / Hard Deletion: Physically deletes stored upload files from disk on demand.
"""
import os
import json
import time
from typing import Dict, Any, Optional, List

RAW_CONSENTED_DIR = "backend/data/raw_consented_uploads"
TRAINING_FEEDBACK_LOG = "backend/data/feedback_dataset.jsonl"

class UploadDataManager:
    """
    Manages consented upload storage and training dataset segregation with hard deletion.
    """
    def __init__(self, raw_dir: str = RAW_CONSENTED_DIR, training_log: str = TRAINING_FEEDBACK_LOG):
        self.raw_dir = raw_dir
        self.training_log = training_log
        os.makedirs(self.raw_dir, exist_ok=True)

    def capture_upload(
        self,
        upload_id: str,
        user_id: str,
        original_text: str,
        cleaned_text: str,
        detection_struct: Dict[str, Any],
        user_consented: bool
    ) -> Dict[str, Any]:
        """
        Processes upload telemetry under strict consent and gating rules.
        """
        # RULE 1: Consent Gate — Absolutely nothing written if user_consented is False
        if not user_consented:
            return {
                "stored_raw": False,
                "stored_training": False,
                "reason": "Consent flag is False. Zero data retained on disk."
            }

        # Pipeline (a): Raw Consented Upload Storage (all consented uploads)
        raw_filepath = os.path.join(self.raw_dir, f"{upload_id}.json")
        raw_record = {
            "upload_id": upload_id,
            "user_id": user_id,
            "timestamp": time.time(),
            "user_consented": True,
            "original_text": original_text,
            "cleaned_text": cleaned_text,
            "detection": detection_struct
        }
        with open(raw_filepath, "w", encoding="utf-8") as f:
            json.dump(raw_record, f, indent=2, ensure_ascii=False)

        # Pipeline (b): Training-Eligible Subset (Gated by 0.05 < P < 0.95 exclusion)
        has_physical_marker = detection_struct.get("stego", False) or detection_struct.get("homoglyph", False)
        synth_risk = detection_struct.get("synthid_risk", 0.0)
        kgw_flagged = detection_struct.get("kgw_flagged", False)

        is_unambiguous = has_physical_marker or (synth_risk >= 0.95) or (synth_risk <= 0.05) or (kgw_flagged and detection_struct.get("kgw_zscore", 0.0) >= 2.5)

        stored_training = False
        if is_unambiguous:
            os.makedirs(os.path.dirname(self.training_log), exist_ok=True)
            training_entry = {
                "upload_id": upload_id,
                "timestamp": time.time(),
                "original_text": original_text,
                "cleaned_text": cleaned_text,
                "detection": detection_struct,
                "is_effective": True
            }
            with open(self.training_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(training_entry, ensure_ascii=False) + "\n")
            stored_training = True

        return {
            "stored_raw": True,
            "raw_filepath": raw_filepath,
            "stored_training": stored_training,
            "training_exclusion_reason": None if stored_training else "Ambiguous confidence (0.05 < P < 0.95) excluded from training buffer to prevent Model Autophagy."
        }

    def delete_upload(self, upload_id: str) -> bool:
        """
        Hard deletion: Physically removes the file from disk.
        """
        target_file = os.path.join(self.raw_dir, f"{upload_id}.json")
        if os.path.exists(target_file):
            try:
                os.remove(target_file)
                return True
            except Exception as e:
                print(f"[-] Failed to physically remove file {target_file}: {e}")
                return False
        return False

    def purge_user_data(self, user_id: str) -> int:
        """
        Hard deletion: Physically removes all files associated with user_id from disk.
        """
        deleted_count = 0
        for fn in os.listdir(self.raw_dir):
            if fn.endswith(".json"):
                fp = os.path.join(self.raw_dir, fn)
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if data.get("user_id") == user_id:
                        os.remove(fp)
                        deleted_count += 1
                except Exception:
                    pass
        return deleted_count

global_upload_manager = UploadDataManager()
