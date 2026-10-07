<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-00C853?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Version-2.0.0-7C4DFF?style=for-the-badge" alt="Version" />
  <img src="https://img.shields.io/badge/Zero%20AI-Pure%20Algorithmic-FF6D00?style=for-the-badge" alt="Zero AI" />
  <img src="https://img.shields.io/badge/License-Research-009688?style=for-the-badge" alt="License" />
</p>

<h1 align="center">🛡️ SORRYLLM</h1>

<h3 align="center">The Sovereign Anti-Watermark Platform for AI-Generated Content</h3>

<p align="center">
  <strong>A 5-Stage Modular Detection & Stripping Pipeline | Multi-Modal Provenance Neutralization Engine</strong>
</p>

<p align="center">
  <em>"Making invisible AI fingerprints visible — then erasing them."</em><br/>
  Zero LLM calls. 100% deterministic. Offline-first. Privacy-sovereign.
</p>

<p align="center">
  <a href="#-project-vision">Project Vision</a> •
  <a href="#-live-architecture-overview">Architecture</a> •
  <a href="#-the-5-stage-neural-pipeline">Pipeline</a> •
  <a href="#-multi-modal-engine-registry">Engine Registry</a> •
  <a href="#-held-out-benchmark-results">Benchmarks</a> •
  <a href="#-local-execution-guide">Quick Start</a>
</p>

---

## 📑 Table of Contents

- [Project Vision](#-project-vision)
- [Live Architecture Overview](#-live-architecture-overview)
- [The 5-Stage Neural Pipeline](#-the-5-stage-neural-pipeline)
- [Multi-Modal Engine Registry](#-multi-modal-engine-registry)
- [Technical Stack](#-technical-stack)
- [Folder Architecture](#-folder-architecture)
- [Core Technical Highlights](#-core-technical-highlights)
- [Held-Out Benchmark Results](#-held-out-benchmark-results)
- [Local Execution Guide](#-local-execution-guide)
- [API Reference](#-api-reference)
- [Security & Data Governance](#-security--data-governance)
- [Innovation Context](#-innovation-context)

---

## 🏛️ Project Vision

**fuckLLM** is a production-grade, offline-first watermark detection and stripping platform — not a simple paraphraser. It functions as a **sovereign anti-forensics engine** that detects, classifies, and surgically removes AI watermarks across **four modalities** (Text, Images, Audio, Video) using pure algorithmic techniques that never introduce new AI signatures.

| Problem | Our Solution |
|:---|:---|
| AI paraphrasers introduce **new** AI signatures while "removing" old ones | 100% non-AI deterministic pipeline — zero LLM calls, zero new fingerprints |
| LLMs hallucinate and make unreliable binary classification | 5-stage modular pipeline with **100% clean specificity** (zero false positives) |
| Invisible zero-width steganography is undetectable to the human eye | Physical Scanner detects and strips **100%** of Unicode steganographic payloads |
| SynthID and KGW watermarks survive simple rewording | Targeted lexical debiasing breaks statistical token-bias distributions |
| No audit trail for what was detected or modified | Every mutation is forensically logged with multi-hop audit trail structs |
| Image provenance (C2PA, EXIF, Stable Signature) survives screenshots | Pixel-matrix reconstruction + VAE grid disruption destroys all embedded provenance |

---

## 🗺️ Live Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                        fuckLLM SOVEREIGN ANTI-WATERMARK PLATFORM                │
│                                                                                  │
│  ┌──────────────────┐   ┌────────────────────────┐   ┌────────────────────────┐  │
│  │   Next.js 14     │──▶│  Next.js API Gateway   │──▶│  FastAPI Microservice  │  │
│  │   React 18       │   │  /api/process/[type]   │   │  http://127.0.0.1:8000 │  │
│  │   Framer Motion  │◀──│  JS Fallback Engine    │◀──│  Command Nexus v2.0   │  │
│  │   Sentient UI    │   │  (works offline!)      │   │  (Python Orchestrator) │  │
│  └──────────────────┘   └───────────┬────────────┘   └───────────┬────────────┘  │
│                                     │                            │                │
│               ┌─────────────────────┼────────────────────────────┤                │
│               │                     │                            │                │
│               ▼                     ▼                            ▼                │
│  ┌────────────────────┐ ┌──────────────────────┐ ┌──────────────────────────┐    │
│  │ DETECTION PIPELINE │ │  STRIPPING ENGINES    │ │  SPECIALIZED MODULES     │    │
│  │                    │ │                       │ │                          │    │
│  │ S1: Physical Scan  │ │ Text: Synonym Swap    │ │ Batch ZIP Processor      │    │
│  │ S2: KGW Z-Score    │ │ Image: Pixel Rebuild  │ │ SLM Neural Rewriter      │    │
│  │ S3: SynthID MLP    │ │ Audio: Time Stretch   │ │ Canary Safety Gate       │    │
│  │ S4: Audit Output   │ │ Video: Frame-by-Frame │ │ Blue/Green Model Deploy  │    │
│  │ S5: Targeted Edit  │ │ PDF/DOCX/SVG/HTML     │ │ Consent-Gated Retraining │    │
│  └────────────────────┘ └──────────────────────┘ └──────────────────────────┘    │
│                                     │                                            │
│                                     ▼                                            │
│               ┌─────────────────────────────────────────┐                        │
│               │           Prisma + SQLite                │                        │
│               │  User Accounts · Job Tracking · Credits  │                        │
│               │  Audit Logs · Transaction Ledger         │                        │
│               └─────────────────────────────────────────┘                        │
└──────────────────────────────────────────────────────────────────────────────────┘
```

> **Fallback Resilience**: If the Python backend is offline, the Next.js API layer executes baseline JavaScript transformations and regex-based invisible-character purging natively — the web app remains **fully functional** for text processing.

---

## ⚡ The 5-Stage Neural Pipeline

```
                                    USER INPUT TEXT
                                           │
                                           ▼
          ┌─────────────────────────────────────────────────────────────────┐
          │ STAGE 1: Deterministic Physical Scanner (< 0.1ms, O(N))        │
          │ • Zero-width Unicode regex (\u200B, \u200C, \u200D, \uFEFF)            │
          │ • Confusables dictionary lookup (confusables_sept2022.json)     │
          │ • Output: {stego: bool, homoglyph: bool}                       │
          └────────────────────────────┬────────────────────────────────────┘
                                       │
                                       ▼
          ┌─────────────────────────────────────────────────────────────────┐
          │ STAGE 2: Closed-Form Statistical Test for KGW (< 0.5ms)        │
          │ • Direct match against GREEN_LIST_MAP synonym substitutions     │
          │ • Exact phrase & multi-word match (filters common corpus words) │
          │ • Binomial Z-score: Z = (k_green - N·p₀) / √(N·p₀·(1-p₀))    │
          │ • Output: {kgw_zscore: float, kgw_flagged: bool}               │
          └────────────────────────────┬────────────────────────────────────┘
                                       │
                                       ▼
          ┌─────────────────────────────────────────────────────────────────┐
          │ STAGE 3: FeatureMLPClassifier for SynthID (< 1ms)              │
          │ • Narrowed 8-D numeric feature vector (n-gram transitions only)│
          │ • MLP Architecture: Linear(8→32)→ReLU→Dropout→Linear(32→16)   │
          │   →ReLU→Linear(16→1)                                           │
          │ • Decoupled from stego/homoglyph/KGW to eliminate gradient     │
          │   starvation — pure SynthID signal learning                    │
          └────────────────────────────┬────────────────────────────────────┘
                                       │
                                       ▼
          ┌─────────────────────────────────────────────────────────────────┐
          │ STAGE 4: Structured Detection Output (Audit-Trail Struct)       │
          │ { stego: bool, homoglyph: bool, kgw_zscore: float,             │
          │   kgw_flagged: bool, synthid_risk: float, synthid_flagged: bool,│
          │   detected_categories: [...], audit_details: {...} }            │
          └────────────────────────────┬────────────────────────────────────┘
                                       │
                                       ▼
          ┌─────────────────────────────────────────────────────────────────┐
          │ STAGE 5: Targeted Editing / Stripping Engine                    │
          │ • Layer A (Physical): Strip zero-width & normalize homoglyphs  │
          │ • Layer B (Statistical): Revert ONLY biased green-synonyms     │
          │ • Feature 1: Contextual discourse connector re-insertion       │
          │ • Multi-hop audit trail for every single mutation               │
          └────────────────────────────┬────────────────────────────────────┘
                                       │
                                       ▼
          ┌─────────────────────────────────────────────────────────────────┐
          │ DATA CAPTURE, CONSENT GATING & RETRAINING SAFETY               │
          │ • Consent Gated: Zero data stored unless user explicitly opts in│
          │ • Ambiguous samples (0.05 < P < 0.95) excluded from training   │
          │ • Immutable 500-sample locked Canary Suite evaluation           │
          │ • Blue/Green atomic promotion with 5-checkpoint rollback        │
          │ • User-controlled hard deletion physically wipes from disk      │
          └─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Multi-Modal Engine Registry

| ID | Engine | Domain | Core Capability | Latency |
|:---|:---|:---|:---|:---|
| **E1** | PureTextStripper | Text Watermarks | 500+ synonym dictionary, invisible char purge, homoglyph normalization, structural restructuring | < 5ms |
| **E2** | StagedWatermarkPipeline | Text Detection | 5-stage modular pipeline: Physical → KGW → SynthID MLP → Audit → Targeted Edit | < 2ms |
| **E3** | FeatureMLPClassifier | SynthID Detection | 8-D feedforward MLP (32→16→1) trained on n-gram transition features | < 1ms |
| **E4** | PureImageStripper | Image Watermarks | 99.8% micro-resize + Lanczos resampling + spatial dither noise (±0.8 RGB) | < 50ms |
| **E5** | MetadataStripper | Provenance Removal | Strips EXIF, IPTC, XMP, C2PA manifests, PNG chunks (caBX, juMB, tEXt, zTXt, iTXt) | < 10ms |
| **E6** | PureAudioStripper | Audio Watermarks | Imperceptible <0.4% micro-speed stretch to break AudioSeal/WavMark correlation | < 100ms |
| **E7** | VideoWatermarkProcessor | Video Watermarks | Frame-by-frame spatial micro-transformations + audio container re-encoding | Variable |
| **E8** | BatchProcessor | Bulk Processing | ZIP archive batch processing — clean multiple files in a single request | Variable |
| **E9** | LayerBParaphraser | Neural Rewriting | Optional SLM-powered paraphrasing layer via local Qwen2.5-0.5B-Instruct | < 500ms |
| **E10** | CanarySafetyGate | Model Governance | 500-sample locked canary suite + atomic blue/green model deployment | N/A |
| **E11** | UploadDataManager | Data Governance | Consent-gated storage with ambiguous-sample exclusion & hard deletion | N/A |
| **E12** | SLMTextGenerator | Text Generation | Local unwatermarked text generation via Qwen2.5-0.5B-Instruct | < 1s |
| **E13** | ContentTypeDetector | Auto-Detection | Magic number / binary signature inspection for automatic media routing | < 0.1ms |

---

## 🛠️ Technical Stack

<table>
<tr>
<td align="center"><strong>🎨 Frontend</strong></td>
<td align="center"><strong>⚙️ Backend & AI</strong></td>
<td align="center"><strong>🗄️ Data & Persistence</strong></td>
<td align="center"><strong>🔒 Security & Governance</strong></td>
</tr>
<tr>
<td>

- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Framer Motion
- Lucide React
- Sharp (image processing)

</td>
<td>

- Python 3.10+
- FastAPI + Uvicorn
- PyTorch (MLP classifier)
- Transformers (SLM)
- OpenCV (headless)
- Pillow + piexif
- NumPy

</td>
<td>

- SQLite via Prisma ORM
- User, Job, CreditTransaction models
- Feedback dataset (JSONL)
- Canary suite (JSON, locked)
- Checkpoint history

</td>
<td>

- Consent-gated data capture
- Ambiguous-sample exclusion
- Hard deletion endpoints
- Blue/Green atomic deploys
- 5-checkpoint rollback
- Multi-hop audit trail

</td>
</tr>
</table>

---

## 🗂️ Folder Architecture

```
fuckLLM/
├── src/
│   └── app/                              # Next.js 14 App Router
│       ├── page.tsx                      # Universal 1-Click Dropzone (Home)
│       ├── layout.tsx                    # Root layout
│       ├── globals.css                   # Cinematic design system
│       ├── text/                         # Dedicated Text Watermark Stripper page
│       ├── image/                        # Image Watermark & Metadata Stripper page
│       ├── audio/                        # Audio Watermark Disruptor page
│       ├── video/                        # Video Frame Processor page
│       ├── dashboard/                    # Usage analytics & job history
│       └── api/process/                  # Next.js API Route Handlers → FastAPI bridge
│           ├── text/route.ts             #   Text processing endpoint
│           ├── image/route.ts            #   Image processing endpoint
│           ├── audio/route.ts            #   Audio processing endpoint
│           └── auto/route.ts             #   Universal auto-detection endpoint
│
├── src/components/
│   ├── navbar.tsx                        # Navigation with animated tabs
│   ├── file-uploader.tsx                 # Drag & drop universal file uploader
│   ├── image-comparison-slider.tsx       # Interactive before/after split slider
│   ├── text-diff-viewer.tsx              # Side-by-side text diff comparison
│   └── ui/                              # Shared UI primitives
│
├── backend/
│   ├── main.py                           # FastAPI orchestrator — 12 REST endpoints
│   ├── pure_text_stripper.py             # 800+ line text watermark removal engine
│   ├── staged_watermark_pipeline.py      # 5-stage modular detection & editing pipeline
│   ├── stage3_synthid_mlp.py             # FeatureMLPClassifier (8-D → 32 → 16 → 1)
│   ├── pure_image_stripper.py            # VAE grid disruption + spatial dither
│   ├── pure_audio_stripper.py            # Micro-speed time stretch engine
│   ├── video_processor.py                # Frame-by-frame video processor
│   ├── metadata_stripper.py              # C2PA/EXIF/XMP/IPTC + PDF/DOCX/SVG/HTML
│   ├── auto_detector.py                  # Content type auto-detection (magic numbers)
│   ├── batch_processor.py                # ZIP archive bulk processor
│   ├── watermark_detector.py             # PyTorch SLM watermark detector
│   ├── ml_stripper_loop.py               # Detector-guided iterative stripping
│   ├── synthid_scorer.py                 # SynthID confidence scoring
│   ├── layer_b_paraphraser.py            # Optional SLM paraphrasing layer
│   ├── slm_text_generator.py             # Local Qwen2.5-0.5B-Instruct generator
│   ├── canary_safety_gate.py             # Canary suite + blue/green deployment gate
│   ├── upload_data_manager.py            # Consent-gated data capture & hard deletion
│   ├── ml_dataset_generator.py           # Training data generation (KGW/SynthID/clean)
│   ├── train_detector.py                 # Model training scripts
│   ├── train_logistic_baseline.py        # Logistic regression baseline comparison
│   ├── eval_staged_pipeline.py           # Pipeline evaluation on held-out data
│   ├── eval_bootstrap.py                 # Bootstrap confidence interval calculation
│   ├── benchmark_stage1_stage2.py        # Stage 1 & 2 benchmark suite
│   ├── verify_features_evidence.py       # Feature engineering verification
│   ├── requirements.txt                  # Python dependencies
│   ├── data/                             # Training data, canary suite, confusables
│   └── models/                           # Trained checkpoints & rollback history
│
├── prisma/
│   ├── schema.prisma                     # Database schema (User, Job, CreditTransaction)
│   └── dev.db                            # SQLite database
│
├── docs/
│   └── ARCHITECTURE.md                   # Detailed 5-stage pipeline architecture
│
├── lm-watermarking/                      # Reference: Kirchenbauer KGW implementation
├── MarkMyWords/                          # Reference: MarkMyWords benchmark suite
├── watermarks-remover/                   # Reference: Alternative watermark removal approaches
│
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── next.config.mjs
└── PROJECT_DOCUMENTATION.md
```

---

## ⚡ Core Technical Highlights

### 1. Deterministic Physical Scanner (Stage 1) — `< 0.1ms`

Scans byte sequences using regex for all invisible Unicode codepoints and confusable homoglyphs:

```
Target Characters:
├── Zero-Width Space       (\u200B)
├── Zero-Width Non-Joiner  (\u200C)
├── Zero-Width Joiner      (\u200D)
├── Byte Order Mark        (\uFEFF)
├── Directional Overrides  (\u200E, \u200F, \u202A–\u202E)
├── Invisible Operators    (\u2060, \u2061–\u2064)
├── Variation Selectors    (\uFE00–\uFE0F)
├── Soft Hyphen            (\u00AD)
├── Tag Characters         (\U000E0020–\U000E007F)  ← binary payload carriers
└── Homoglyphs             Cyrillic а→a, е→e, о→o, р→p, с→c (+ 40 more)
```

**Result**: 100% deterministic precision and recall on intact markers.

---

### 2. Closed-Form KGW Statistical Test (Stage 2) — `< 0.5ms`

Standard LLMs can't reliably detect green-list token biases. Our engine uses direct synonym mapping against the **exact generation dictionary**:

```
Input:  "AI systems guarantee state-of-the-art data collection"
                   │            │                 │
                   ▼            ▼                 ▼
         ┌─────────────┐ ┌──────────────┐ ┌───────────────┐
         │ GREEN_LIST   │ │ GREEN_LIST   │ │ GREEN_LIST    │
         │ ensure →     │ │ modern →     │ │ dataset →     │
         │ "guarantee"  │ │ "state-of-   │ │ "data         │
         │              │ │  the-art"    │ │  collection"  │
         └─────────────┘ └──────────────┘ └───────────────┘

Binomial Z-score: Z = (k_green - N·p₀) / √(N·p₀·(1-p₀))
If Z > threshold → KGW_FLAGGED = true
```

**Result**: 8.3× recall improvement over monolithic baseline (7.8% → 64.7%).

---

### 3. FeatureMLPClassifier for SynthID (Stage 3) — `< 1ms`

```python
# 8-Dimensional Feature Vector (decoupled from stego/homoglyph/KGW)
features = [
    marker_hits,        # SynthID signature transitional phrase count
    marker_density,     # Phrase hit density per sentence
    transition_hits,    # Formal connector count (furthermore, moreover...)
    transition_density, # Connector density per word
    avg_sentence_len,   # Normalized average sentence length
    sent_len_var,       # Normalized sentence length variance
    ttr,                # Type-Token Ratio (vocabulary richness)
    punct_density       # Formal punctuation cadence
]

# MLP Architecture
Linear(8 → 32) → ReLU → Dropout(0.1) → Linear(32 → 16) → ReLU → Linear(16 → 1)
```

**Key Insight**: By completely removing stego, homoglyph, and KGW features from the input, the MLP focuses **100%** of gradient signal on learning subtle n-gram boundary shifts — eliminating gradient starvation.

---

### 4. Multi-Modal Provenance Destruction

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        IMAGE PIPELINE                                   │
│                                                                         │
│  Input Image ──► Pixel Matrix Extraction ──► Clean Image Reconstruction │
│       │                                              │                  │
│       ├── EXIF Metadata ──────────── STRIPPED         │                  │
│       ├── IPTC Metadata ──────────── STRIPPED         │                  │
│       ├── XMP Metadata ───────────── STRIPPED         │                  │
│       ├── C2PA Manifest ──────────── STRIPPED         │                  │
│       ├── PNG Chunks (caBX/juMB) ─── STRIPPED         │                  │
│       │                                              │                  │
│       └── 99.8% Micro-Resize + Lanczos Resampling ──►│                  │
│           + Spatial Dither Noise (±0.8 RGB)           │                  │
│           = VAE Latent Grid DESTROYED                 │                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  DOCUMENT CONTAINERS: PDF · DOCX · SVG · HTML · Markdown               │
│  ──────────────────────────────────────────────────────                  │
│  PDF  → Binary stream reconstruction, metadata block removal            │
│  DOCX → XML namespace purge (core.xml, app.xml properties)              │
│  SVG  → <metadata>, <desc>, xmlns:dc namespace stripping                │
│  HTML → <meta name="generator"> tag removal                             │
│  MD   → YAML frontmatter extraction & invisible char purge              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 5. Retraining Safety & Canary Validation Gate

To protect against **Model Autophagy** and feedback poisoning:

```
[Candidate Model] ──► [Canary Suite (500 locked samples, seed=1337)]
                              │
            ┌─────────────────┼──────────────────┐
            ▼                 ▼                  ▼
    ┌───────────────┐ ┌──────────────┐ ┌────────────────┐
    │ Clean Spec    │ │ Stego/Hybrid │ │ SynthID Recall │
    │ ≥ 95.0%      │ │ ≥ 99.0%      │ │ ≥ 90.0%        │
    └───────┬───────┘ └──────┬───────┘ └────────┬───────┘
            │                │                  │
            └────────────────┼──────────────────┘
                             │
                    ┌────────┴────────┐
                    │   ALL PASSED?   │
                    └────────┬────────┘
               ┌─────────YES─┴─NO──────────┐
               ▼                            ▼
    ┌────────────────────┐      ┌────────────────────┐
    │ Atomic Promotion   │      │ REJECTED           │
    │ → active checkpoint│      │ Regression alert   │
    │ → archive prior    │      │ Prior model kept   │
    │ → 5-gen rollback   │      │                    │
    └────────────────────┘      └────────────────────┘
```

---

## 📊 Held-Out Benchmark Results

**Full 5-Stage Pipeline Evaluation** (N=750, held-out test set, never seen during training):

```
══════════════════════════════════════════════════════════════════════════════
FULL 5-STAGE PIPELINE EVALUATION ON HELD-OUT TEST SET (N=750)
══════════════════════════════════════════════════════════════════════════════
Category           │ Raw Counts   │ Recall / Specificity [95% CI]    │ Precision [95% CI]
───────────────────┼──────────────┼──────────────────────────────────┼─────────────────────
clean              │ 374/374      │ Spec:  100.0% [100.0% - 100.0%] │ N/A
steganography      │  98/ 98      │ Recall:100.0% [100.0% - 100.0%] │ 100.0% [100.0% - 100.0%]
hybrid             │  97/ 97      │ Recall:100.0% [100.0% - 100.0%] │ 100.0% [100.0% - 100.0%]
synthid_ngram      │  73/ 79      │ Recall: 92.4% [ 86.1% -  97.5%] │ 100.0% [100.0% - 100.0%]
kgw_token_bias     │  66/102      │ Recall: 64.7% [ 54.9% -  74.5%] │ 100.0% [100.0% - 100.0%]
══════════════════════════════════════════════════════════════════════════════
```

### Comparison Against Previous Monolithic Baseline

| Category | Previous 17-D Monolithic MLP | **New 5-Stage Modular Pipeline** | Delta |
|:---|:---|:---|:---|
| **Clean Specificity** | 92.2% [89.6% - 94.9%] | **100.0% [100.0% - 100.0%]** (0/374 FP) | ✅ **+7.8% (Zero False Positives)** |
| **Steganography** | 100.0% | **100.0%** (98/98) | ✅ Match |
| **Hybrid** | 100.0% | **100.0%** (97/97) | ✅ Match |
| **SynthID N-Gram** | 93.7% [87.3% - 98.7%] | **92.4%** [86.1% - 97.5%] (73/79) | ✅ Within 95% CI |
| **KGW Token-Bias** | 7.8% [2.9% - 13.7%] | **64.7%** [54.9% - 74.5%] (66/102) | ✅ **8.3× Recall Improvement** |

> **Key Achievement**: Zero false positives on clean text (100% specificity) while achieving 8.3× improvement on the hardest watermark category (KGW token-bias).

---

## 🚀 Local Execution Guide

### Prerequisites

| Requirement | Version | Purpose |
|:---|:---|:---|
| **Node.js** | 18+ | Next.js frontend runtime |
| **Python** | 3.10+ | FastAPI backend + PyTorch |
| **pip** | Latest | Python package manager |
| **CUDA** *(optional)* | 11.8+ | GPU acceleration for MLP & SLM |

### Step 1 — Clone & Install

```bash
git clone https://github.com/Vishnummmmmmmm/llmwatermark.git
cd llmwatermark

# Install Python dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install Node dependencies
npm install
```

### Step 2 — Initialize Database

```bash
npx prisma generate
npx prisma db push
```

### Step 3 — Launch Platform

```bash
# Terminal 1 — Start FastAPI Orchestrator (port 8000)
cd backend
python main.py

# Terminal 2 — Start Next.js Frontend (port 3000)
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)** — the platform is live.

> 💡 **Tip**: The frontend works independently for basic text cleaning even without the Python backend running. Start both services for full multi-modal processing + ML detection.

### Step 4 — Ingest Training Data *(optional)*

```bash
# Generate synthetic watermarked + clean training pairs
cd backend
python ml_dataset_generator.py

# Train the FeatureMLPClassifier
python train_detector.py

# Evaluate on held-out test set
python eval_staged_pipeline.py
```

---

## 📡 API Reference

All endpoints served by FastAPI at `http://127.0.0.1:8000`:

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/health` | Health check — returns `{status: "online", mode: "Pure-Non-AI", version: "2.0.0"}` |
| `POST` | `/api/process/auto` | Universal auto-detection — routes text/image/audio/video/PDF/DOCX/SVG/HTML/ZIP automatically |
| `POST` | `/api/process/text` | Text watermark stripping with configurable synonym swap ratio, restructuring, Layer B |
| `POST` | `/api/process/ml-detect` | SynthID/KGW/Stego detection via 5-stage pipeline — returns structured audit JSON |
| `POST` | `/api/process/ml-strip` | Detector-guided iterative stripping with continuous learning feedback logging |
| `GET` | `/api/process/ml-stats` | Model stats: architecture info, training status, feedback queue size |
| `POST` | `/api/generate` | Generate clean unwatermarked text via local SLM (Qwen2.5-0.5B-Instruct) |
| `POST` | `/api/rewrite` | Rewrite watermarked text naturally using local SLM neural editor |

### Example: Text Processing

```bash
curl -X POST http://127.0.0.1:8000/api/process/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "It is crucial to note that AI systems utilize multifaceted frameworks.",
    "synonymSwapRatio": 0.35,
    "restructureSentences": true,
    "stripInvisible": true
  }'
```

**Response:**
```json
{
  "cleaned_text": "It is key to note that AI systems use complex frameworks.",
  "invisible_chars_found": 0,
  "invisible_chars_removed": 0,
  "homoglyphs_normalized": 0,
  "synonyms_swapped": 2,
  "structures_modified": 0,
  "audit_trail": [
    {"original": "crucial", "replacement": "key", "type": "synonym_swap"},
    {"original": "utilize", "replacement": "use", "type": "synonym_swap"}
  ]
}
```

### Example: ML Detection

```bash
curl -X POST http://127.0.0.1:8000/api/process/ml-detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Furthermore, it is crucial to note that from a structural standpoint..."}'
```

**Response:**
```json
{
  "is_watermarked": true,
  "stego": false,
  "homoglyph": false,
  "kgw_zscore": 1.82,
  "kgw_flagged": false,
  "synthid_risk": 0.89,
  "synthid_flagged": true,
  "detected_categories": ["synthid_ngram"],
  "audit_details": {
    "invisible_char_count": 0,
    "homoglyph_count": 0,
    "synthid_markers_found": ["from a structural standpoint", "it is crucial to note that"]
  }
}
```

---

## 🔒 Security & Data Governance

| Layer | Implementation | Details |
|:---|:---|:---|
| **Consent Gate** | Explicit opt-in flag | Zero bytes written to disk unless `user_consented = True` |
| **Training Segregation** | Ambiguous-sample exclusion | Only P ≤ 0.05 or P ≥ 0.95 admitted to training set |
| **Model Safety** | Canary Suite (500 locked) | Immutable evaluation set (seed=1337), never in training pool |
| **Deployment** | Blue/Green atomic swap | Candidate must pass all threshold gates before promotion |
| **Rollback** | 5-checkpoint history | Instant rollback to any of prior 5 model versions |
| **Hard Deletion** | Physical file wipe | User-triggered deletion physically removes all stored data from disk |
| **Audit Trail** | Multi-hop mutation log | Every single text transformation forensically logged with provenance |
| **Fallback** | JS in-process engine | Text processing works even if Python backend is completely offline |

---

## 🏆 Innovation Context

This project demonstrates interdisciplinary engineering at the intersection of three disciplines:

```
 Adversarial ML  ×  Signal Processing  ×  Information Security
 ─────────────────────────────────────────────────────────────────
 MLP Classifier       VAE Grid Disruption       Zero-Width Stego
 KGW Z-Score           Lanczos Resampling       Homoglyph Detection
 SynthID Features      Micro-Speed Stretch      Unicode Forensics
 Canary Validation     Spatial Dither Noise     Consent-Gated Data
 Blue/Green Deploy     Pixel Reconstruction     Audit Trail Struct
```

### Impact Thesis

> Every piece of AI-generated content is now fingerprinted — by Google (SynthID), by Kirchenbauer et al. (KGW), by invisible Unicode steganography, by C2PA metadata manifests. These watermarks are designed to be invisible and indelible. **fuckLLM proves they are neither.**

---

<p align="center">
  <strong>Built with 🔥 using Next.js 14 · FastAPI · PyTorch · Pure Algorithmic Processing</strong>
</p>

<p align="center">
  <em>Deterministic. Sovereign. Zero-AI. Production-Ready.</em>
</p>

<p align="center">
  © 2026 fuckLLM — Privacy-First Anti-Watermark Platform
</p>
