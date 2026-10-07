# fuckLLM — AI Watermark & Provenance Removal System
## End-to-End System Architecture & Operating Guide

---

### 1. Executive Overview

**fuckLLM** is an offline, privacy-first, 100% pure non-AI algorithmic watermark stripping and metadata removal platform. It targets and neutralizes synthetic provenance markers across four major modalities: **Text**, **Images**, **Audio**, and **Video**. 

Unlike conventional AI paraphrasers or regenerators that introduce new AI signatures, fuckLLM relies on deterministic mathematical, statistical, structural, and signal-processing techniques to destroy watermarks without calling external LLM APIs.

---

### 2. High-Level Architecture

```
                          ┌─────────────────────────────────────────┐
                          │         Next.js 14 Frontend             │
                          │   (Tailwind CSS + Framer Motion UI)     │
                          └────────────────────┬────────────────────┘
                                               │
                                               ▼
                          ┌─────────────────────────────────────────┐
                          │          Next.js Route Handlers         │
                          │  (/api/process/[text|image|audio|auto]) │
                          └────────────────────┬────────────────────┘
                                               │ (HTTP Proxy / Fallback)
                                               ▼
                          ┌─────────────────────────────────────────┐
                          │      FastAPI Python Microservice        │
                          │        (http://127.0.0.1:8000)          │
                          └────────────────────┬────────────────────┘
                                               │
            ┌──────────────────┬───────────────┴───────────────┬──────────────────┐
            ▼                  ▼                               ▼                  ▼
┌──────────────────────┐ ┌─────────────────────┐ ┌───────────────────┐ ┌────────────────────┐
│  Pure Text Stripper  │ │ Pure Image Stripper │ │Pure Audio Stripper│ │Video Frame Stripper│
│(Synonyms, Stego-Purge│ │(Micro-Resizing,EXIF)│ │(Micro-Speed Shift)│ │(Frame-wise Clean)  │
└──────────────────────┘ └─────────────────────┘ └───────────────────┘ └────────────────────┘
```

---

### 3. Component Breakdown

#### A. Next.js 14 Frontend (`/src/app`)
- **Technology Stack**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide React, Framer Motion.
- **Key Routes**:
  - `/`: Universal 1-Click Dropzone with automatic file/text content detection.
  - `/text`: Dedicated Text Watermark Stripper featuring 100% Zero-Width Invisible Watermark Purger and real-time side-by-side text diff viewer (`text-diff-viewer.tsx`).
  - `/image`: Dedicated Image Watermark & Metadata Stripper featuring an interactive before/after split slider (`image-comparison-slider.tsx`).
  - `/audio`: Dedicated Audio Watermark Disruptor (neutralizes Meta AudioSeal and WavMark).
  - `/video`: Video frame-by-frame and audio container processor.
  - `/dashboard`: Usage analytics and job history tracking via Prisma SQLite.

#### B. API Gateway & Fallback Layer (`/src/app/api/process/*`)
- Serves as the interface between the web client and the backend processing engines.
- Proxies requests to the local Python FastAPI microservice (`http://127.0.0.1:8000/api/process/*`).
- Includes **In-Process Fallbacks**: If the FastAPI microservice is offline, Next.js executes baseline pure-JavaScript transformations and regex invisible-character purging natively so the web application remains functional.

#### C. Python FastAPI Microservice (`/backend`)
- **`main.py`**: REST API server running on port `8000`. Exposes CORS-enabled endpoints (`/api/process/auto`, `/api/process/text`, etc.).
- **`auto_detector.py`**: Inspects magic numbers / binary signatures and text content to automatically determine media types.

---

### 4. Pure Algorithmic Watermark Stripping Engines

#### 1. Text & Invisible LLM Watermark Removal (`backend/pure_text_stripper.py`)
- **Target Watermarks**: 
  - **Invisible Zero-Width & Steganography Watermarks**: Zero Width Space (`\u200B`), Zero Width Non-Joiner (`\u200C`), Zero Width Joiner (`\u200D`), Byte Order Mark (`\uFEFF`), Directional Overrides (`\u202A`–`\u202E`), Variation Selectors (`\uFE00`–`\uFE0F`), Tag Characters (`\U000E0020`–`\U000E007F` for binary payloads), and Homoglyph substitution.
  - **Statistical Token-Bias Watermarks**: SynthID-Text (Google), KGW (Kirchenbauer et al.) Green-List/Red-List token biases, BIRA.
- **Stripping Mechanism**:
  1. **100% Invisible Character Purge & Homoglyph Normalization**: Scans text via regular expressions for all zero-width characters, invisible operators, and control tags, stripping 100% of hidden steganographic payload bits. Normalizes look-alike Cyrillic/Greek homoglyphs to standard NFKC / ASCII letters.
  2. **Green/Red List Breakout**: Performs probabilistic synonym substitution using a curated offline dictionary (`OFFLINE_SYNONYM_DICT`), altering green-list token distributions.
  3. **Structural Restructuring**: Splices and restructures sentence syntax at conjunction points to break n-gram positional probability scores.
  4. **Zero-Width Hash Perturbation**: Inserts controlled hash-breaking tweaks if enabled to defeat rigid string-matching detectors.

#### 2. Image Watermark & Metadata Removal (`backend/pure_image_stripper.py` & `metadata_stripper.py`)
- **Target Watermarks**: Stable Signature (VAE latent watermarks), C2PA, EXIF, IPTC, and XMP metadata headers.
- **Stripping Mechanism**:
  1. **100% Metadata Scrubbing**: Reconstructs raw pixel data matrices into clean streams, completely stripping EXIF, IPTC, XMP, and Adobe C2PA manifests.
  2. **VAE Latent Grid Disruption**: Performs a 99.8% micro-resize followed by Lanczos resampling back to original dimensions, destroying pixel-grid aligned spatial frequencies used by VAE decoder signatures.
  3. **Spatial Dither Noise**: Adds micro-dither noise ($\pm 0.8$ level across RGB channels) to scramble embedded message bits without visual quality degradation.

#### 3. Audio Watermark Removal (`backend/pure_audio_stripper.py`)
- **Target Watermarks**: Meta AudioSeal, WavMark.
- **Stripping Mechanism**:
  1. **Micro-Speed Time Stretch**: Applies an imperceptible <0.4% speed modification (e.g. 0.996x stretch). This shifts exact temporal sample indices ($1/16,000\text{s}$ sample grid), causing correlation-based detectors to fail.
  2. **Spectral Phase Perturbation**: Injects subtle acoustic dither noise to neutralize phase-encoded audio signatures.

#### 4. Video Watermark Removal (`backend/video_processor.py`)
- **Stripping Mechanism**: Processes video streams frame-by-frame using spatial micro-transformations combined with audio container re-encoding.

---

### 5. Data Persistence (`/prisma/schema.prisma`)

- **Database Engine**: SQLite (`prisma/dev.db`).
- **Models**:
  - `User`: Manages user accounts, credit balances, and timestamps.
  - `Job`: Tracks media processing tasks (`type`, `status`, `inputData`, `outputData`, `metrics`, `creditsUsed`).
  - `CreditTransaction`: Records credit purchases and deductions.

---

### 6. End-to-End Operational Workflow

```
[User Action] (Paste LLM text containing hidden zero-width markers or drop file into Web UI at http://localhost:3000)
       │
       ▼
[Next.js API Gateway] (/api/process/text or /api/process/auto)
       │
       ▼
[FastAPI Backend / PureTextStripper] (backend/pure_text_stripper.py)
       │
 ┌─────┴────────────────────────────────────────────────────────────────────────┐
 │ 1. Steganography Purge: \u200B, \u200C, \uFEFF, \u200E, \u200F, \u2060, Tag Chars stripped 100% │
 │ 2. Homoglyph Normalization: Cyrillic/Greek look-alikes normalized to Latin   │
 │ 3. Offline Synonym Swap: Green-list logit distributions broken               │
 │ 4. Structural Restructuring & Controlled Hash Break                          │
 └──────────────────────────────────────┬───────────────────────────────────────┘
                                        │
                                        ▼
                   [Response Payload Returned to Frontend]
                                        │
                                        ▼
      [Interactive UI Rendering with Invisible Purge Banner & Token Diffs]
```

---

### 7. How to Run the Project Locally

#### 1. Backend Microservice (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python main.py
```
*Runs on `http://127.0.0.1:8000`*

#### 2. Frontend Application (Next.js)
```bash
# In the root directory
npm install
npm run dev
```
*Runs on `http://localhost:3000`*

---
