"""
staged_watermark_pipeline.py — Staged Watermark Detection & Targeted Editing Pipeline

Clean, modular 5-stage architecture:
- Stage 1: Deterministic Physical Scanner (<0.1ms, zero-width + homoglyphs)
- Stage 2: Closed-Form Statistical Test for KGW (<0.5ms, direct synonym match + binomial Z-score)
- Stage 3: FeatureMLPClassifier for SynthID (<1ms, narrowed n-gram features only)
- Stage 4: Structured Detection Output (Audit-trail struct)
- Stage 5: Targeted Editing / Stripping (Layer A physical normalization + Layer B targeted lexical replacement)
"""
import os
import re
import json
import torch
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
INVISIBLE_PATTERN = re.compile(
    r'[\u200B\u200C\u200D\uFEFF\u200E\u200F\u2060\u2061-\u2064\uFE00-\uFE0F\u00AD\U000E0020-\U000E007F]'
)

CONFUSABLES_PATH = os.path.join(os.path.dirname(__file__), "data", "confusables_sept2022.json")

def load_confusable_map(path: str = CONFUSABLES_PATH) -> Dict[str, str]:
    """Loads and inverts the Unicode confusable mapping table."""
    reverse_map = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for target_char, confusables in data.items():
            if len(target_char) == 1 and ord(target_char) < 128:
                for conf in confusables:
                    if len(conf) == 1 and ord(conf) >= 128:
                        reverse_map[conf] = target_char
    # Ensure Cyrillic homoglyph mappings are present
    cyrillic_map = {
        'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'у': 'y', 'х': 'x',
        'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M', 'Н': 'N', 'О': 'O',
        'Р': 'P', 'С': 'C', 'Т': 'T', 'Х': 'X'
    }
    reverse_map.update(cyrillic_map)
    return reverse_map

CONFUSABLE_MAP = load_confusable_map()

# KGW Synonym Mappings (matching generator dictionary)
try:
    from ml_dataset_generator import GREEN_LIST_MAP
except ImportError:
    GREEN_LIST_MAP = {
        "transforming": ["revolutionizing", "reshaping", "modifying"],
        "landscape": ["terrain", "framework", "environment"],
        "technology": ["systems", "tech", "innovation"],
        "modern": ["contemporary", "state-of-the-art", "current"],
        "complex": ["intricate", "elaborate", "sophisticated"],
        "scalable": ["expandable", "elastic", "flexible"],
        "converts": ["transforms", "translates", "renders"],
        "dataset": ["corpus", "data collection", "data repository"],
        "datasets": ["corpora", "data collections", "data repositories"],
        "models": ["networks", "architectures", "systems"],
        "ensure": ["guarantee", "assure", "secure"],
        "requires": ["demands", "necessitates", "calls for"],
        "understand": ["comprehend", "discern", "perceive"],
        "protect": ["safeguard", "shield", "defend"],
        "rapidly": ["swiftly", "quickly", "acceleratedly"],
        "rely": ["depend", "count", "hinge"],
        "manage": ["govern", "administer", "orchestrate"],
        "provide": ["furnish", "offer", "deliver"],
        "expands": ["broadens", "amplifies", "extends"]
    }

STOP_WORDS = {"for", "in", "the", "a", "an", "and", "or", "of", "to", "with"}
BASE_CORPUS_WORDS = {"data", "systems", "architectures"}

# Exact phrases and words for KGW direct matching
EXACT_GREEN_PHRASES = []
EXACT_GREEN_WORDS = set()
# Map each green synonym back to its canonical clean base word for Stage 5 targeted replacement
REVERSE_GREEN_MAP = {}

for base_w, syns in GREEN_LIST_MAP.items():
    for syn in syns:
        clean_syn = syn.lower().strip()
        REVERSE_GREEN_MAP[clean_syn] = base_w
        # Also store punctuation-stripped key
        stripped_key = re.sub(r'[^\w]', '', clean_syn)
        if stripped_key != clean_syn:
            REVERSE_GREEN_MAP[stripped_key] = base_w
            
        if " " in clean_syn or "-" in clean_syn:
            EXACT_GREEN_PHRASES.append(clean_syn)
        else:
            w = re.sub(r'[^\w]', '', clean_syn)
            if w and w not in STOP_WORDS and w not in BASE_CORPUS_WORDS:
                EXACT_GREEN_WORDS.add(w)

# Sort phrases by length descending for greedy replacement
EXACT_GREEN_PHRASES = sorted(EXACT_GREEN_PHRASES, key=lambda x: len(x), reverse=True)

SYNTHID_MARKERS = [
    "in terms of overall execution",
    "significantly speaking",
    "from a structural standpoint",
    "indeed, it is crucial to note that",
    "it is crucial to note that",
    "essentially,"
]

TRANSITION_CONNECTORS = {
    "furthermore", "moreover", "consequently", "subsequently", "specifically",
    "conversely", "notwithstanding", "accordingly", "ultimately", "essentially"
}

# Contextual Word Re-Insertion dictionaries for natural human cadence
CONTEXTUAL_CONNECTORS = [
    "Notably,",
    "In practice,",
    "Clearly,",
    "As observed,",
    "Ultimately,"
]

# Natural human contextual synonyms for enriched variation (preserving exact semantic intent)
CONTEXTUAL_ENRICHMENT_MAP = {
    "transforming": ["advancing", "reshaping", "driving change in"],
    "landscape": ["domain", "ecosystem", "sphere"],
    "complex": ["multifaceted", "demanding", "advanced"],
    "scalable": ["adaptable", "versatile", "growth-ready"],
    "converts": ["channels", "processes", "translates"],
    "dataset": ["sample set", "data collection", "curated data"],
    "ensure": ["maintain", "foster", "reinforce"],
    "requires": ["calls for", "depends on", "involves"],
    "understand": ["analyze", "interpret", "evaluate"],
    "protect": ["safeguard", "secure", "preserve"],
    "rapidly": ["steadily", "substantially", "actively"],
    "manage": ["coordinate", "guide", "direct"],
    "provide": ["deliver", "support", "enable"],
    "expands": ["deepens", "enhances", "broadens"]
}

SYNTHID_FEATURE_DIM = 8

# ==============================================================================
# STAGE 3: FeatureMLPClassifier Definition
# ==============================================================================
class FeatureMLPClassifier(torch.nn.Module):
    """
    Feedforward Multi-Layer Perceptron (MLP) trained on hand-engineered numeric features
    specifically for SynthID n-gram & transitional phrase detection.
    """
    def __init__(self, input_dim: int = SYNTHID_FEATURE_DIM, hidden_dim: int = 32):
        super(FeatureMLPClassifier, self).__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(input_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.1),
            torch.nn.Linear(hidden_dim, hidden_dim // 2),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim // 2, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ==============================================================================
# PIPELINE IMPLEMENTATION
# ==============================================================================
class StagedWatermarkPipeline:
    """
    Unified 5-Stage Staged Watermark Detection & Targeted Stripping Pipeline.
    """
    def __init__(self, model_weights_path: Optional[str] = None):
        self.model = FeatureMLPClassifier(input_dim=SYNTHID_FEATURE_DIM, hidden_dim=32)
        
        default_path = os.path.join(os.path.dirname(__file__), "models", "synthid_feature_mlp.pt")
        weights_to_load = model_weights_path or default_path
        
        if os.path.exists(weights_to_load):
            self.model.load_state_dict(torch.load(weights_to_load, map_location="cpu"))
            self.model.eval()
            self.is_model_loaded = True
        else:
            self.is_model_loaded = False

    # --------------------------------------------------------------------------
    # STAGE 1: Deterministic Physical Scanner (<0.1ms)
    # --------------------------------------------------------------------------
    def stage1_scan_physical(self, text: str) -> Dict[str, Any]:
        """
        Stage 1: Deterministic Physical Scanner (<0.1ms).
        Inspects raw bytes for zero-width stego and homoglyphs.
        """
        stego_matches = INVISIBLE_PATTERN.findall(text)
        has_stego = len(stego_matches) > 0
        
        homoglyph_matches = [c for c in text if c in CONFUSABLE_MAP]
        has_homoglyph = len(homoglyph_matches) > 0
        
        return {
            "stego": has_stego,
            "stego_count": len(stego_matches),
            "homoglyph": has_homoglyph,
            "homoglyph_count": len(homoglyph_matches)
        }

    # --------------------------------------------------------------------------
    # STAGE 2: Closed-Form Statistical Test for KGW (<0.5ms)
    # --------------------------------------------------------------------------
    def stage2_kgw_statistical_test(self, text: str, z_threshold: float = 1.8, min_hits: int = 1) -> Dict[str, Any]:
        """
        Stage 2: Closed-Form Statistical Test for KGW (<0.5ms).
        Direct match against GREEN_LIST_MAP and binomial Z-score computation.
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
        
        # Baseline rate p_0 on clean text for these rare synonyms
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

    # --------------------------------------------------------------------------
    # STAGE 3: FeatureMLPClassifier for SynthID (<1ms)
    # --------------------------------------------------------------------------
    def extract_synthid_features(self, text: str) -> np.ndarray:
        """Extracts narrowed 8-D SynthID feature vector."""
        lower_text = text.lower()
        words = [re.sub(r'[^\w]', '', w).lower() for w in text.split() if w]
        n_words = max(1, len(words))
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        n_sentences = max(1, len(sentences))
        
        marker_hits = sum(1 for m in SYNTHID_MARKERS if m in lower_text)
        marker_density = marker_hits / n_sentences
        
        transition_hits = sum(1 for w in words if w in TRANSITION_CONNECTORS)
        transition_density = transition_hits / n_words
        
        sent_lens = [len(s.split()) for s in sentences]
        avg_sent_len = float(np.mean(sent_lens)) if sent_lens else 0.0
        sent_len_var = float(np.var(sent_lens)) if len(sent_lens) > 1 else 0.0
        
        unique_words = len(set(words))
        ttr = unique_words / n_words
        
        punct_count = len(re.findall(r'[,;:\-–—]', text))
        punct_density = punct_count / n_words
        
        return np.array([
            float(marker_hits),
            float(marker_density),
            float(transition_hits),
            float(transition_density),
            avg_sent_len / 20.0,
            min(1.0, sent_len_var / 100.0),
            float(ttr),
            float(punct_density)
        ], dtype=np.float32)

    def stage3_synthid_classify(self, text: str, threshold: float = 0.50) -> Dict[str, Any]:
        """
        Stage 3: FeatureMLPClassifier for SynthID N-Gram Bias.
        """
        feats = self.extract_synthid_features(text)
        
        matched_markers = [m for m in SYNTHID_MARKERS if m in text.lower()]
        
        if self.is_model_loaded:
            with torch.no_grad():
                tensor_x = torch.tensor(feats, dtype=torch.float32).unsqueeze(0)
                prob = float(torch.sigmoid(self.model(tensor_x)).item())
        else:
            prob = 1.0 if len(matched_markers) > 0 else 0.0
            
        is_flagged = prob >= threshold
        
        return {
            "synthid_risk": round(prob, 4),
            "synthid_flagged": bool(is_flagged),
            "matched_markers": matched_markers
        }

    # --------------------------------------------------------------------------
    # STAGE 4: Structured Detection Output (Audit-Trail Struct)
    # --------------------------------------------------------------------------
    def detect(self, text: str) -> Dict[str, Any]:
        """
        Runs Stage 1 -> Stage 2 -> Stage 3 (if ambiguous) and compiles Stage 4 structured audit struct.
        No downstream clamping or probability distortion.
        """
        s1 = self.stage1_scan_physical(text)
        s2 = self.stage2_kgw_statistical_test(text)
        s3 = self.stage3_synthid_classify(text)
        
        detected_categories = []
        if s1["stego"]: detected_categories.append("invisible_steganography")
        if s1["homoglyph"]: detected_categories.append("homoglyph_substitution")
        if s2["kgw_flagged"]: detected_categories.append("kgw_token_bias")
        if s3["synthid_flagged"]: detected_categories.append("synthid_ngram")
        
        is_watermarked = len(detected_categories) > 0
        
        return {
            "is_watermarked": is_watermarked,
            "stego": s1["stego"],
            "homoglyph": s1["homoglyph"],
            "kgw_zscore": s2["kgw_zscore"],
            "kgw_flagged": s2["kgw_flagged"],
            "synthid_risk": s3["synthid_risk"],
            "synthid_flagged": s3["synthid_flagged"],
            "detected_categories": detected_categories if is_watermarked else ["clean"],
            "audit_details": {
                "invisible_char_count": s1["stego_count"],
                "homoglyph_count": s1["homoglyph_count"],
                "kgw_green_matches": s2["matched_words"],
                "synthid_markers_found": s3["matched_markers"]
            }
        }

    # --------------------------------------------------------------------------
    # STAGE 5: Targeted Editing / Stripping Engine & Contextual Enrichment
    # --------------------------------------------------------------------------
    def stage5_targeted_strip(
        self,
        text: str,
        detection_result: Optional[Dict] = None,
        enable_enrichment: bool = True,
        enrich_substitutions: bool = False
    ) -> Dict[str, Any]:
        """
        Stage 5: Targeted Editing / Stripping & Contextual Word Re-Insertion.
        
        - Layer A (physical): Strips zero-width chars and normalizes homoglyphs to ASCII. No sentence rewriting.
        - Layer B (statistical): Targeted replacement of ONLY the biased green-synonyms and SynthID phrases.
          Preserves unaffected sentences and surrounding words exactly.
        - Contextual Enrichment:
          * enable_enrichment=True, enrich_substitutions=False (Mode A - Default):
            Re-inserts natural discourse connectors strictly at spans where SynthID markers were stripped.
            Does NOT re-touch words Stage 5 already de-biased via GREEN_LIST_MAP.
          * enable_enrichment=True, enrich_substitutions=True (Mode B - Extended):
            Also provides varied contextual synonyms for de-biased words.
            
        - Multi-Hop Audit Trail:
          Logs each stage's edits distinctly without collapsing intermediate transformations.
        """
        if detection_result is None:
            detection_result = self.detect(text)
            
        current_text = text
        audit_trail = []
        
        # --- Layer A: Physical Normalization ---
        if detection_result.get("stego", False):
            cleaned = INVISIBLE_PATTERN.sub('', current_text)
            removed_count = len(current_text) - len(cleaned)
            if removed_count > 0:
                audit_trail.append({
                    "span": "<invisible_characters>",
                    "type": "invisible_steganography",
                    "stage5_edit": f"Removed {removed_count} zero-width codepoints",
                    "feature1_edit": None,
                    "final": "<stripped>",
                    "stages_applied": ["Stage 5 (Layer A Physical)"]
                })
                current_text = cleaned
                
        if detection_result.get("homoglyph", False):
            normalized_chars = []
            replaced_homoglyphs = 0
            for c in current_text:
                if c in CONFUSABLE_MAP:
                    normalized_chars.append(CONFUSABLE_MAP[c])
                    replaced_homoglyphs += 1
                else:
                    normalized_chars.append(c)
            if replaced_homoglyphs > 0:
                audit_trail.append({
                    "span": "<confusable_homoglyphs>",
                    "type": "homoglyph_substitution",
                    "stage5_edit": f"Normalized {replaced_homoglyphs} homoglyphs to Latin",
                    "feature1_edit": None,
                    "final": "<normalized>",
                    "stages_applied": ["Stage 5 (Layer A Physical)"]
                })
                current_text = "".join(normalized_chars)

        # Normalize AI em-dashes (—), en-dashes (–), and spaced hyphens
        dash_matches = re.findall(r'\s*[—–―]\s*|(?<=\w)\s+-\s+(?=\w)', current_text)
        if dash_matches:
            dash_cleaned = re.sub(r'(\w)\s*[—–―]\s*(\w)', r'\1, \2', current_text)
            dash_cleaned = re.sub(r'(\w)\s+-\s+(\w)', r'\1, \2', dash_cleaned)
            dash_cleaned = re.sub(r'^\s*[—–―-]\s*', '', dash_cleaned, flags=re.MULTILINE)
            dash_cleaned = re.sub(r'\s*[—–―-]\s*$', '', dash_cleaned, flags=re.MULTILINE)
            dash_cleaned = re.sub(r',\s*,+', ',', dash_cleaned)
            dash_cleaned = re.sub(r',\s*\.', '.', dash_cleaned)
            dash_cleaned = re.sub(r'\s+,', ',', dash_cleaned)
            audit_trail.append({
                "span": "<em_dash_markers>",
                "type": "em_dash_normalization",
                "stage5_edit": f"Normalized {len(dash_matches)} em-dash/en-dash markers",
                "feature1_edit": None,
                "final": "<normalized>",
                "stages_applied": ["Stage 5 (Layer A Physical)"]
            })
            current_text = dash_cleaned
                
        # --- Layer B: Targeted Lexical & N-Gram Replacement ---
        # If the sample is watermarked, inspect and clean any exposed SynthID or KGW markers in the normalized text
        if detection_result.get("is_watermarked", False):
            # 1. SynthID Targeted Phrase Removal / Re-Insertion
            for marker in SYNTHID_MARKERS:
                pattern = re.compile(re.escape(marker), re.IGNORECASE)
                if pattern.search(current_text):
                    if enable_enrichment:
                        # Re-insert natural connector at the stripped slot
                        conn_idx = abs(hash(marker)) % len(CONTEXTUAL_CONNECTORS)
                        replacement_conn = " " + CONTEXTUAL_CONNECTORS[conn_idx]
                        current_text = pattern.sub(replacement_conn, current_text, count=1)
                        audit_trail.append({
                            "span": marker,
                            "type": "synthid_ngram",
                            "stage5_edit": "<stripped_transitional_phrase>",
                            "feature1_edit": CONTEXTUAL_CONNECTORS[conn_idx],
                            "final": CONTEXTUAL_CONNECTORS[conn_idx],
                            "stages_applied": ["Stage 5 (Removal)", "Feature 1 (Re-Insertion)"]
                        })
                    else:
                        current_text = pattern.sub('', current_text)
                        audit_trail.append({
                            "span": marker,
                            "type": "synthid_ngram",
                            "stage5_edit": "<stripped_transitional_phrase>",
                            "feature1_edit": None,
                            "final": "<removed>",
                            "stages_applied": ["Stage 5 (Removal)"]
                        })
            # Clean up double spaces or orphan punctuation
            current_text = re.sub(r' +', ' ', current_text)
            current_text = re.sub(r'\s+([,.:;])', r'\1', current_text)
            
            # 2. KGW Targeted Synonym Reversion / Enriched Re-Insertion
            # First pass: Multi-word and hyphenated green phrases
            for phrase in EXACT_GREEN_PHRASES:
                pattern = re.compile(rf'\b{re.escape(phrase)}\b', re.IGNORECASE)
                if pattern.search(current_text):
                    base_canonical = REVERSE_GREEN_MAP.get(phrase, REVERSE_GREEN_MAP.get(re.sub(r'[^\w]', '', phrase), "modern"))
                    if enable_enrichment and enrich_substitutions and base_canonical in CONTEXTUAL_ENRICHMENT_MAP:
                        syn_options = CONTEXTUAL_ENRICHMENT_MAP[base_canonical]
                        chosen_syn = syn_options[0]
                        current_text = pattern.sub(chosen_syn, current_text)
                        audit_trail.append({
                            "span": phrase,
                            "type": "kgw_token_bias",
                            "stage5_edit": base_canonical,
                            "feature1_edit": chosen_syn,
                            "final": chosen_syn,
                            "stages_applied": ["Stage 5 (Debias Substitution)", "Feature 1 (Enrichment Paraphrase)"]
                        })
                    else:
                        current_text = pattern.sub(base_canonical, current_text)
                        audit_trail.append({
                            "span": phrase,
                            "type": "kgw_token_bias",
                            "stage5_edit": base_canonical,
                            "feature1_edit": None,
                            "final": base_canonical,
                            "stages_applied": ["Stage 5 (Debias Substitution)"]
                        })

            # Second pass: Word-level green synonyms
            words = current_text.split()
            new_words = []
            for idx_w, w in enumerate(words):
                clean_w = re.sub(r'[^\w]', '', w).lower()
                punct_suffix = w[len(clean_w):] if w.lower().startswith(clean_w) else ""
                
                if clean_w in REVERSE_GREEN_MAP:
                    base_canonical = REVERSE_GREEN_MAP[clean_w]
                    
                    if enable_enrichment and enrich_substitutions and base_canonical in CONTEXTUAL_ENRICHMENT_MAP:
                        # Mode B: Multi-hop substitution (green -> canonical base -> contextual synonym)
                        syn_options = CONTEXTUAL_ENRICHMENT_MAP[base_canonical]
                        chosen_syn = syn_options[idx_w % len(syn_options)]
                        replacement = chosen_syn
                        if w and w[0].isupper():
                            replacement = replacement.capitalize()
                        new_words.append(replacement + punct_suffix)
                        audit_trail.append({
                            "span": clean_w,
                            "type": "kgw_token_bias",
                            "stage5_edit": base_canonical,
                            "feature1_edit": chosen_syn,
                            "final": replacement,
                            "stages_applied": ["Stage 5 (Debias Substitution)", "Feature 1 (Enrichment Paraphrase)"]
                        })
                    else:
                        # Mode A (Default): Single-hop debiasing (green -> canonical base)
                        replacement = base_canonical
                        if w and w[0].isupper():
                            replacement = replacement.capitalize()
                        new_words.append(replacement + punct_suffix)
                        audit_trail.append({
                            "span": clean_w,
                            "type": "kgw_token_bias",
                            "stage5_edit": base_canonical,
                            "feature1_edit": None,
                            "final": replacement,
                            "stages_applied": ["Stage 5 (Debias Substitution)"]
                        })
                else:
                    new_words.append(w)
            current_text = " ".join(new_words)

        # Formatting cleanup
        if audit_trail:
            current_text = re.sub(r'\.\s*\.', '.', current_text)
            current_text = re.sub(r'\s+,', ',', current_text)
            current_text = re.sub(r' +', ' ', current_text)
            sentences = re.split(r'(\. |\? |\! )', current_text)
            enriched_sentences = []
            for s in sentences:
                if s and s[0].islower() and not s.startswith(('.', '?', '!')):
                    enriched_sentences.append(s[0].upper() + s[1:])
                else:
                    enriched_sentences.append(s)
            current_text = "".join(enriched_sentences)
            
        diff_summary = f"Applied {len(audit_trail)} targeted modification(s)." if audit_trail else "No modifications required."
        
        return {
            "original_text": text,
            "cleaned_text": current_text.strip(),
            "is_modified": len(audit_trail) > 0,
            "edits_applied": audit_trail,
            "diff_summary": diff_summary
        }
