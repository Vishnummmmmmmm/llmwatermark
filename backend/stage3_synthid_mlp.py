"""
Stage 3: FeatureMLPClassifier for SynthID N-Gram Bias Detection
Trained strictly on narrowed SynthID/structural feature set (no stego/homoglyph/KGW-hash features).
"""
import os
import re
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from typing import Dict, List, Tuple

# SynthID characteristic transitional phrases
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

SYNTHID_FEATURE_DIM = 8

class FeatureMLPClassifier(nn.Module):
    """
    Feedforward Multi-Layer Perceptron (MLP) trained on hand-engineered numeric features
    specifically for SynthID n-gram & transitional phrase detection.
    """
    def __init__(self, input_dim: int = SYNTHID_FEATURE_DIM, hidden_dim: int = 32):
        super(FeatureMLPClassifier, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

def extract_synthid_features(text: str) -> np.ndarray:
    """
    Extracts strictly SynthID-relevant numeric features.
    No stego, homoglyph, or KGW-hash features.
    """
    lower_text = text.lower()
    words = [re.sub(r'[^\w]', '', w).lower() for w in text.split() if w]
    n_words = max(1, len(words))
    
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    n_sentences = max(1, len(sentences))
    
    # 1. Exact SynthID phrase marker count
    marker_hits = sum(1 for m in SYNTHID_MARKERS if m in lower_text)
    marker_density = marker_hits / n_sentences
    
    # 2. Transition connector words count & density
    transition_hits = sum(1 for w in words if w in TRANSITION_CONNECTORS)
    transition_density = transition_hits / n_words
    
    # 3. Sentence length statistics
    sent_lens = [len(s.split()) for s in sentences]
    avg_sent_len = float(np.mean(sent_lens)) if sent_lens else 0.0
    sent_len_var = float(np.var(sent_lens)) if len(sent_lens) > 1 else 0.0
    
    # 4. Vocabulary richness (Type-Token Ratio)
    unique_words = len(set(words))
    ttr = unique_words / n_words
    
    # 5. Punctuation cadence
    punct_count = len(re.findall(r'[,;:\-–—]', text))
    punct_density = punct_count / n_words
    
    features = np.array([
        float(marker_hits),
        float(marker_density),
        float(transition_hits),
        float(transition_density),
        avg_sent_len / 20.0,
        min(1.0, sent_len_var / 100.0),
        float(ttr),
        float(punct_density)
    ], dtype=np.float32)
    
    return features

def train_and_benchmark_stage3():
    train_path = "backend/data/train_data.json"
    heldout_path = "backend/data/test_data_heldout.json"
    
    with open(train_path, "r", encoding="utf-8") as f:
        train_data = json.load(f)
    with open(heldout_path, "r", encoding="utf-8") as f:
        heldout_data = json.load(f)
        
    print(f"\n{'='*100}")
    print(f"STAGE 3: TRAINING & BENCHMARKING FeatureMLPClassifier FOR SYNTHID")
    print(f"{'='*100}")
    
    # Filter training data: clean vs synthid
    X_train_list, y_train_list = [], []
    for s in train_data:
        wtype = s.get("watermark_type", "clean")
        if wtype in ("clean", "synthid_ngram"):
            feats = extract_synthid_features(s["text"])
            lbl = 1.0 if wtype == "synthid_ngram" else 0.0
            X_train_list.append(feats)
            y_train_list.append(lbl)
            
    X_train = torch.tensor(np.array(X_train_list), dtype=torch.float32)
    y_train = torch.tensor(np.array(y_train_list), dtype=torch.float32).unsqueeze(1)
    
    # Balance positive weighting
    n_pos = float(torch.sum(y_train == 1.0).item())
    n_neg = float(torch.sum(y_train == 0.0).item())
    pos_weight = torch.tensor([n_neg / max(1.0, n_pos)], dtype=torch.float32)
    
    dataset = TensorDataset(X_train, y_train)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    torch.manual_seed(42)
    model = FeatureMLPClassifier(input_dim=SYNTHID_FEATURE_DIM, hidden_dim=32)
    optimizer = optim.AdamW(model.parameters(), lr=0.01, weight_decay=1e-4)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    
    model.train()
    for epoch in range(50):
        for bx, by in loader:
            optimizer.zero_grad()
            logits = model(bx)
            loss = criterion(logits, by)
            loss.backward()
            optimizer.step()
            
    # Save trained FeatureMLPClassifier checkpoint
    os.makedirs("backend/models", exist_ok=True)
    torch.save(model.state_dict(), "backend/models/synthid_feature_mlp.pt")
    print("Saved FeatureMLPClassifier to backend/models/synthid_feature_mlp.pt")
    
    # Benchmark on heldout test set
    model.eval()
    
    # 1. Evaluate SynthID recall on held-out test set
    synthid_samples = [s for s in heldout_data if s.get("watermark_type") == "synthid_ngram"]
    clean_samples = [s for s in heldout_data if s.get("watermark_type") == "clean"]
    
    synth_scores = []
    with torch.no_grad():
        for s in synthid_samples:
            feats = torch.tensor(extract_synthid_features(s["text"]), dtype=torch.float32).unsqueeze(0)
            prob = float(torch.sigmoid(model(feats)).item())
            synth_scores.append(prob)
            
    clean_scores = []
    with torch.no_grad():
        for s in clean_samples:
            feats = torch.tensor(extract_synthid_features(s["text"]), dtype=torch.float32).unsqueeze(0)
            prob = float(torch.sigmoid(model(feats)).item())
            clean_scores.append(prob)
            
    synth_preds = [1 if p >= 0.50 else 0 for p in synth_scores]
    clean_preds = [1 if p >= 0.50 else 0 for p in clean_scores]
    
    raw_synth_hits = sum(synth_preds)
    raw_clean_fps = sum(clean_preds)
    
    synth_rec = raw_synth_hits / len(synthid_samples)
    clean_spec = (len(clean_samples) - raw_clean_fps) / len(clean_samples)
    
    # Bootstrap CI
    from benchmark_stage1_stage2 import bootstrap_metric, recall_fn, spec_fn
    rec, r_lo, r_hi = bootstrap_metric(np.ones(len(synthid_samples)), np.array(synth_preds), recall_fn)
    spec, s_lo, s_hi = bootstrap_metric(np.zeros(len(clean_samples)), np.array(clean_preds), spec_fn)
    
    print(f"\n--- STAGE 3 BENCHMARK RESULTS (Held-Out N={len(heldout_data)}) ---")
    print(f"SynthID Recall:     {rec*100:.1f}% [{r_lo*100:.1f}% - {r_hi*100:.1f}%] (Raw: {raw_synth_hits}/{len(synthid_samples)})")
    print(f"Clean Specificity:  {spec*100:.1f}% [{s_lo*100:.1f}% - {s_hi*100:.1f}%] (False Positives: {raw_clean_fps}/{len(clean_samples)})")
    print(f"Previous Baseline:  93.7% [87.3% - 98.7%]")
    
    if rec >= 0.937:
        print(">>> SUCCESS: FeatureMLPClassifier matches or beats previous 93.7% baseline!")
    else:
        print(f">>> NOTICE: Recall is {rec*100:.1f}% (target >= 93.7%).")

if __name__ == "__main__":
    train_and_benchmark_stage3()
