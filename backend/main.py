"""
fuckLLM Python Processing API Gateway
FastAPI server implementing PURE NON-AI watermark & provenance removal pipelines.
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64

from pure_text_stripper import PureTextStripper
from pure_image_stripper import PureImageStripper
from pure_audio_stripper import PureAudioStripper
from auto_detector import ContentTypeDetector
from video_processor import VideoWatermarkProcessor
from metadata_stripper import MetadataStripper

app = FastAPI(
    title="fuckLLM Pure Non-AI Watermark Removal API",
    version="2.0.0",
    description="REST microservice performing pure algorithmic non-AI watermark stripping"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pure_text_engine = PureTextStripper()
pure_image_engine = PureImageStripper()
pure_audio_engine = PureAudioStripper()
video_engine = VideoWatermarkProcessor()

from synthid_scorer import SynthIDScorer
from batch_processor import BatchProcessor
from layer_b_paraphraser import LayerBParaphraser

batch_engine = BatchProcessor()

class TextProcessRequest(BaseModel):
    text: str
    synonymSwapRatio: float = 0.35
    restructureSentences: bool = True
    characterTweak: bool = True
    stripInvisible: bool = True
    useLayerB: bool = False

@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "online", "mode": "Pure-Non-AI", "version": "2.0.0"}

@app.post("/api/process/auto")
async def process_auto(
    file: UploadFile = File(None),
    text: str = Form(None)
):
    """Universal auto-detection endpoint"""
    if text and text.strip():
        # Process as pure non-AI text
        res = pure_text_engine.strip_text_watermark(text=text)
        return {"detected_type": "text", "result": res}
    
    if file:
        contents = await file.read()
        fn = (file.filename or "").lower()

        # Check if zip batch archive
        if fn.endswith(".zip"):
            cleaned_zip_bytes, batch_summary = batch_engine.process_zip_archive(contents)
            clean_b64 = base64.b64encode(cleaned_zip_bytes).decode("utf-8")
            return {
                "detected_type": "batch_zip",
                "result": {
                    "download_url": f"data:application/zip;base64,{clean_b64}",
                    "files_processed": batch_summary["files_processed"],
                    "summary_items": batch_summary["summary_items"],
                    "removal_summary": f"Cleaned {batch_summary['files_processed']} file(s) inside zip archive."
                }
            }

        detected_type = ContentTypeDetector.detect_file_type(contents, file.filename or "")

        if detected_type == "container":
            if fn.endswith(".pdf") or contents.startswith(b"%PDF"):
                clean_bytes, meta = MetadataStripper.strip_pdf_metadata(contents)
                clean_b64 = base64.b64encode(clean_bytes).decode("utf-8")
                return {
                    "detected_type": "container",
                    "container_format": "PDF",
                    "result": {
                        "cleaned_file": f"data:application/pdf;base64,{clean_b64}",
                        "meta": meta,
                        "removal_summary": f"PDF metadata purged. {len(meta.get('findings', []))} action(s) taken."
                    }
                }
            elif fn.endswith(".docx") or contents.startswith(b"PK\x03\x04"):
                clean_bytes, meta = MetadataStripper.strip_docx_metadata(contents)
                clean_b64 = base64.b64encode(clean_bytes).decode("utf-8")
                return {
                    "detected_type": "container",
                    "container_format": "DOCX",
                    "result": {
                        "cleaned_file": f"data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{clean_b64}",
                        "meta": meta,
                        "removal_summary": f"DOCX container xml metadata purged. {len(meta.get('findings', []))} action(s) taken."
                    }
                }
            elif fn.endswith(".svg"):
                text_str = contents.decode("utf-8", errors="ignore")
                clean_text, meta = MetadataStripper.strip_svg_metadata(text_str)
                return {
                    "detected_type": "container",
                    "container_format": "SVG",
                    "result": {
                        "cleaned_text": clean_text,
                        "meta": meta,
                        "removal_summary": f"SVG metadata purged. {len(meta.get('findings', []))} block(s) stripped."
                    }
                }
            elif fn.endswith(".html") or fn.endswith(".htm"):
                text_str = contents.decode("utf-8", errors="ignore")
                clean_text, meta = MetadataStripper.strip_html_metadata(text_str)
                return {
                    "detected_type": "container",
                    "container_format": "HTML",
                    "result": {
                        "cleaned_text": clean_text,
                        "meta": meta,
                        "removal_summary": f"HTML generator tags purged."
                    }
                }
            else:
                text_str = contents.decode("utf-8", errors="ignore")
                clean_text, meta = MetadataStripper.strip_markdown_frontmatter(text_str)
                res = pure_text_engine.strip_text_watermark(clean_text)
                return {
                    "detected_type": "container",
                    "container_format": "Markdown",
                    "result": {
                        "cleaned_text": res["cleaned_text"],
                        "meta": meta,
                        "text_result": res,
                        "removal_summary": f"Markdown frontmatter & Unicode steganography purged."
                    }
                }

        if detected_type == "image":
            pre_meta = MetadataStripper.inspect_metadata(contents)
            clean_bytes = pure_image_engine.strip_image(contents)
            post_meta = MetadataStripper.inspect_metadata(clean_bytes)

            synthid_score_pre = SynthIDScorer.calculate_confidence_score(contents, pre_meta.get("has_c2pa", False))
            synthid_score_post = SynthIDScorer.calculate_confidence_score(clean_bytes, False)

            detected_items = []
            if pre_meta.get("has_exif"): detected_items.append("EXIF Metadata")
            if pre_meta.get("has_xmp"): detected_items.append("XMP Metadata")
            if pre_meta.get("has_c2pa"): detected_items.append("C2PA Manifest")

            total_found = len(detected_items)
            removal_pct = 100.0 if total_found > 0 else 0.0

            orig_b64 = base64.b64encode(contents).decode("utf-8")
            clean_b64 = base64.b64encode(clean_bytes).decode("utf-8")
            return {
                "detected_type": "image",
                "result": {
                    "originalUrl": f"data:image/jpeg;base64,{orig_b64}",
                    "cleanedUrl": f"data:image/jpeg;base64,{clean_b64}",
                    "pre_metadata": pre_meta,
                    "post_metadata": post_meta,
                    "synthid_score_pre": synthid_score_pre,
                    "synthid_score_post": synthid_score_post,
                    "detected_items": detected_items,
                    "total_detected_metadata": total_found,
                    "removal_percentage": removal_pct,
                    "removal_summary": f"SynthID risk reduced from {synthid_score_pre}% to {synthid_score_post}%. {total_found} metadata item(s) scrubbed."
                }
            }
        elif detected_type == "audio":
            res = pure_audio_engine.strip_audio(contents)
            return {"detected_type": "audio", "result": res}
        elif detected_type == "video":
            res = video_engine.process_video_frames(contents)
            return {"detected_type": "video", "result": res}
        else:
            # Fallback text
            try:
                decoded = contents.decode("utf-8")
                res = pure_text_engine.strip_text_watermark(decoded)
                return {"detected_type": "text", "result": res}
            except Exception:
                raise HTTPException(status_code=400, detail="Unsupported media format")

    raise HTTPException(status_code=400, detail="Must provide either text or file")

from watermark_detector import global_detector
from ml_stripper_loop import global_ml_stripper, FEEDBACK_LOG_PATH
import os

@app.post("/api/process/text")
def process_text(req: TextProcessRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    res = pure_text_engine.strip_text_watermark(
        text=req.text,
        synonym_swap_ratio=req.synonymSwapRatio,
        restructure_sentences=req.restructureSentences,
        character_tweak=req.characterTweak,
        strip_invisible=req.stripInvisible
    )
    if req.useLayerB:
        rewritten, used_ollama = LayerBParaphraser.paraphrase_text(res["cleaned_text"])
        res["cleaned_text"] = rewritten
        res["layer_b_applied"] = True
        res["layer_b_ollama"] = used_ollama
    return res

@app.post("/api/process/ml-detect")
def process_ml_detect(req: TextProcessRequest):
    """
    Analyzes text using PyTorch SLM Watermark Detector to return watermark confidence score and detected anomaly types.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    detection = global_detector.detect(req.text)
    return detection

@app.post("/api/process/ml-strip")
def process_ml_strip(req: TextProcessRequest):
    """
    Detector-Guided Iterative Text Stripping Engine with Continuous Learning Feedback Logging.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    result = global_ml_stripper.process_text_with_feedback(req.text)
    return result

@app.get("/api/process/ml-stats")
def get_ml_stats():
    """
    Returns current FeatureMLPClassifier stats, feedback queue size, and model trained status.
    """
    feedback_count = 0
    if os.path.exists(FEEDBACK_LOG_PATH):
        try:
            with open(FEEDBACK_LOG_PATH, "r", encoding="utf-8") as f:
                feedback_count = sum(1 for _ in f)
        except Exception:
            feedback_count = 0

    return {
        "status": "active",
        "model_architecture": "FeatureMLPClassifier (8-D feedforward neural net for SynthID n-gram detection)",
        "is_model_trained": global_detector.is_trained,
        "checkpoint_path": global_detector.checkpoint_path,
        "feedback_pairs_logged": feedback_count
    }

from slm_text_generator import get_slm_generator

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 150

class RewriteRequest(BaseModel):
    text: str

@app.post("/api/generate")
def generate_unwatermarked_text(req: GenerateRequest):
    """
    Generates clean, unwatermarked text on-demand using local SLM (Qwen2.5-0.5B-Instruct).
    """
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    generator = get_slm_generator()
    generated = generator.generate_text(req.prompt, max_tokens=req.max_tokens)
    return {
        "prompt": req.prompt,
        "generated_text": generated,
        "model": generator.model_id
    }

@app.post("/api/rewrite")
def rewrite_text_slm(req: RewriteRequest):
    """
    Rewrites watermarked or flagged text naturally using local SLM neural editor.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    generator = get_slm_generator()
    rewritten = generator.rewrite_sentence(req.text)
    return {
        "original_text": req.text,
        "rewritten_text": rewritten,
        "model": generator.model_id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


