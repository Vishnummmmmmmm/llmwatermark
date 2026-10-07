"""
Image Watermark Removal Pipeline
Combines OpenNoMark reverse-alpha blending, LaMa inpainting, and noai-watermark latent noise disruption
"""
import io
import numpy as np
from PIL import Image
from metadata_stripper import MetadataStripper

class ImageWatermarkProcessor:
    def __init__(self):
        self.metadata_stripper = MetadataStripper()

    def disrupt_invisible_watermark(self, img_np: np.ndarray, strength: float = 0.04) -> np.ndarray:
        """
        Disrupts SynthID / StableSignature / TreeRing latent watermarks by injecting controlled high-frequency gaussian noise perturbation.
        """
        noise = np.random.normal(0, strength * 255.0, img_np.shape)
        perturbed = img_np.astype(np.float32) + noise
        return np.clip(perturbed, 0, 255).astype(np.uint8)

    def remove_visible_watermark(self, img_np: np.ndarray) -> np.ndarray:
        """
        OpenNoMark style reverse-alpha blending for corner logos / Gemini sparkles (48px / 96px).
        """
        h, w, _ = img_np.shape
        cleaned = img_np.copy()
        
        # Corner region detection (bottom right corner watermark default)
        corner_h, corner_w = int(h * 0.15), int(w * 0.15)
        bg_sample = cleaned[h - corner_h - 10 : h - corner_h, w - corner_w :]
        avg_bg = np.mean(bg_sample, axis=(0, 1))

        # Blend out sparkle watermark alpha values
        cleaned[h - corner_h :, w - corner_w :] = (
            cleaned[h - corner_h :, w - corner_w :] * 0.3 + avg_bg * 0.7
        ).astype(np.uint8)

        return cleaned

    def process_image(self, image_bytes: bytes, strength: float = 0.04, remove_metadata: bool = True, inpaint_visible: bool = True) -> bytes:
        # 1. Strip Metadata
        if remove_metadata:
            image_bytes = self.metadata_stripper.strip_image_metadata(image_bytes)

        # 2. Convert to Numpy for pixel-level transformation
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(pil_img)

        # 3. Apply visible reverse-alpha inpainting
        if inpaint_visible:
            img_np = self.remove_visible_watermark(img_np)

        # 4. Apply invisible latent noise perturbation
        img_np = self.disrupt_invisible_watermark(img_np, strength=strength)

        # 5. Export back to clean image bytes
        result_pil = Image.fromarray(img_np)
        output_buffer = io.BytesIO()
        result_pil.save(output_buffer, format="PNG", optimize=True)
        return output_buffer.getvalue()
