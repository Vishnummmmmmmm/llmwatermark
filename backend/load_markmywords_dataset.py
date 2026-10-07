"""
MarkMyWords Dataset Importer & Converter for fuckLLM PyTorch SLM Detector.
Loads clean prompt samples from MarkMyWords repository (MarkMyWords/src/watermark_benchmark/low_entropy_tasks.json)
and generates paired clean vs watermarked training data.
"""
import os
import json
import argparse
from ml_dataset_generator import WatermarkDatasetGenerator

MARKMYWORDS_TASKS_PATH = "MarkMyWords/src/watermark_benchmark/low_entropy_tasks.json"
OUTPUT_DATASET_PATH = "backend/data/watermark_dataset.json"

def convert_markmywords_to_training_set(
    source_json_path: str = MARKMYWORDS_TASKS_PATH,
    output_json_path: str = OUTPUT_DATASET_PATH,
    max_samples: int = 500
):
    """
    Parses clean texts from MarkMyWords repository and builds balanced clean (0) vs watermarked (1) PyTorch dataset.
    """
    if not os.path.exists(source_json_path):
        print(f"[-] MarkMyWords source file not found at: {source_json_path}")
        return False

    with open(source_json_path, "r", encoding="utf-8") as f:
        clean_texts = json.load(f)

    print(f"[+] Loaded {len(clean_texts)} base texts from MarkMyWords repository.")

    generator = WatermarkDatasetGenerator()
    dataset = []
    
    count = 0
    for text in clean_texts:
        if count >= max_samples:
            break

        # Trim text to ~500 chars for clean token sequences
        clean_text = text[:800].strip()
        if len(clean_text) < 50:
            continue

        # Pair 1: Clean sample (label 0)
        dataset.append({
            "id": f"mmw_clean_{count}",
            "text": clean_text,
            "label": 0,
            "watermark_type": "clean",
            "source": "MarkMyWords"
        })

        # Pair 2: Watermarked sample (label 1)
        wm_type = "kgw_token_bias" if count % 2 == 0 else "steganography"
        if wm_type == "kgw_token_bias":
            wm_text = generator.apply_kgw_watermark(clean_text, bias_ratio=0.55)
        else:
            wm_text = generator.apply_steganography_watermark(clean_text)

        dataset.append({
            "id": f"mmw_wm_{count}",
            "text": wm_text,
            "label": 1,
            "watermark_type": wm_type,
            "source": "MarkMyWords"
        })

        count += 1

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"[+] Successfully converted {len(dataset)} paired samples from MarkMyWords!")
    print(f"[+] Dataset saved to: {output_json_path}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert MarkMyWords repo tasks to fuckLLM dataset")
    parser.add_argument("--source", type=str, default=MARKMYWORDS_TASKS_PATH, help="Source JSON path")
    parser.add_argument("--output", type=str, default=OUTPUT_DATASET_PATH, help="Output JSON path")
    parser.add_argument("--samples", type=int, default=500, help="Max base samples")
    args = parser.parse_args()

    convert_markmywords_to_training_set(args.source, args.output, args.samples)
