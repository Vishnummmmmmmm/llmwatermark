"""
Synthetic Paired Text Watermark Dataset Generator
Generates clean vs watermarked text pairs (KGW green-list token bias, SynthID n-gram bias, zero-width steganography, and homoglyphs)
for training and fine-tuning the PyTorch Watermark Detector SLM.
"""
import os
import re
import json
import random
import argparse
from typing import List, Dict, Tuple

# Sample base clean sentences & paragraphs for data generation
BASE_CLEAN_CORPUS = [
    "Artificial intelligence is transforming the landscape of modern technology and software engineering.",
    "The rain in Spain falls mainly on the plain, creating lush green valleys across the countryside.",
    "Quantum computing leverages superposition and entanglement to solve complex computational problems.",
    "To build scalable web applications, developers use modern microservices architectures and robust databases.",
    "Photosynthesis converts light energy into chemical energy, providing fuel for living organisms.",
    "Machine learning models require clean datasets, proper hyperparameter tuning, and rigorous validation.",
    "The history of civilization is filled with dramatic discoveries, artistic achievements, and cultural shifts.",
    "Distributed database systems ensure fault tolerance, high availability, and horizontal scalability.",
    "Natural language processing enables computers to understand, interpret, and generate human language.",
    "Cybersecurity protocols protect sensitive user data from unauthorized access, breach, and interception.",
    "Solar power and wind energy are rapidly becoming the primary drivers of sustainable global infrastructure.",
    "Effective communication between client and server relies on standardized HTTP protocols and serialization.",
    "Deep learning architectures like transformers rely on self-attention mechanisms to process sequential data.",
    "The economic impact of global trade agreements shapes supply chains across international markets.",
    "Modern operating systems manage hardware resources, memory allocation, and process scheduling efficiently.",
    "Cryptographic algorithms ensure data privacy through symmetric encryption and public key infrastructure.",
    "Biomedical research has advanced significantly due to genomic sequencing and computational biology.",
    "Space exploration expands our understanding of planetary systems, cosmic radiation, and stellar evolution.",
    "Software design patterns provide reusable solutions to common object-oriented architectural challenges.",
    "Mobile applications must optimize battery consumption, network bandwidth, and local storage utilization."
]

# Green list synonym mappings for KGW token bias simulation
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

# Zero width & invisible steganography chars
INVISIBLE_CHARS = ['\u200B', '\u200C', '\u200D', '\uFEFF', '\u200E', '\u200F', '\u2060']

# Homoglyph replacements
HOMOGLYPHS = {'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'c': 'с', 'y': 'у', 'x': 'х'}


class WatermarkDatasetGenerator:
    """
    Generates synthetic watermarked text samples paired with clean originals.
    """

    def apply_kgw_watermark(self, text: str, bias_ratio: float = 0.5) -> str:
        """
        Simulates Kirchenbauer et al. (KGW) Red/Green list token bias by systematically
        shifting word choice toward green-list synonyms.
        """
        words = text.split()
        watermarked_words = []
        for word in words:
            clean_w = re.sub(r'[^\w]', '', word).lower()
            if clean_w in GREEN_LIST_MAP and random.random() < bias_ratio:
                synonym = random.choice(GREEN_LIST_MAP[clean_w])
                if word[0].isupper():
                    synonym = synonym.capitalize()
                # preserve trailing punctuation
                punct = word[len(clean_w):] if len(word) > len(clean_w) else ""
                watermarked_words.append(synonym + punct)
            else:
                watermarked_words.append(word)
        return " ".join(watermarked_words)

    def apply_synthid_watermark(self, text: str) -> str:
        """
        Simulates SynthID-Text n-gram distribution bias by inserting characteristic
        transitional phrasing and specific statistical token patterns.
        """
        markers = [
            " In terms of overall execution,",
            " Significantly speaking,",
            " From a structural standpoint,",
            " Indeed, it is crucial to note that",
            " Essentially,"
        ]
        sentences = text.split('. ')
        if len(sentences) > 1:
            idx = random.randint(0, len(sentences) - 1)
            sentences[idx] += random.choice(markers)
        return '. '.join(sentences)

    def apply_steganography_watermark(self, text: str) -> str:
        """
        Injects zero-width invisible unicode payload characters and homoglyph substitutions.
        """
        chars = list(text)
        num_injections = max(2, len(chars) // 15)
        for _ in range(num_injections):
            pos = random.randint(0, len(chars) - 1)
            inv_char = random.choice(INVISIBLE_CHARS)
            chars[pos] = chars[pos] + inv_char
        
        # Inject homoglyphs
        for i in range(len(chars)):
            if chars[i] in HOMOGLYPHS and random.random() < 0.15:
                chars[i] = HOMOGLYPHS[chars[i]]
                
        return "".join(chars)

    def generate_dataset(self, num_samples: int = 400) -> List[Dict]:
        """
        Generates paired dataset containing balanced clean (0) and watermarked (1) examples.
        """
        dataset = []
        
        for i in range(num_samples):
            # Select base clean text
            base_text = random.choice(BASE_CLEAN_CORPUS)
            # Create a multi-sentence sample
            extra_sentence = random.choice(BASE_CLEAN_CORPUS)
            if base_text != extra_sentence:
                base_text += " " + extra_sentence

            if i % 2 == 0:
                # Clean sample
                dataset.append({
                    "id": f"sample_{i}",
                    "text": base_text,
                    "label": 0,
                    "watermark_type": "clean",
                    "original_text": base_text
                })
            else:
                # Watermarked sample
                wm_type = random.choice(["kgw_token_bias", "synthid_ngram", "steganography", "hybrid"])
                wm_text = base_text
                
                if wm_type == "kgw_token_bias":
                    wm_text = self.apply_kgw_watermark(base_text, bias_ratio=0.6)
                elif wm_type == "synthid_ngram":
                    wm_text = self.apply_synthid_watermark(base_text)
                elif wm_type == "steganography":
                    wm_text = self.apply_steganography_watermark(base_text)
                elif wm_type == "hybrid":
                    wm_text = self.apply_kgw_watermark(base_text, bias_ratio=0.4)
                    wm_text = self.apply_steganography_watermark(wm_text)
                    
                dataset.append({
                    "id": f"sample_{i}",
                    "text": wm_text,
                    "label": 1,
                    "watermark_type": wm_type,
                    "original_text": base_text
                })
                
        random.shuffle(dataset)
        return dataset

def main():
    parser = argparse.ArgumentParser(description="Generate PyTorch Watermark Detector dataset")
    parser.add_argument("--samples", type=int, default=500, help="Number of dataset samples to generate")
    parser.add_argument("--output", type=str, default="backend/data/watermark_dataset.json", help="Output file path")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    generator = WatermarkDatasetGenerator()
    dataset = generator.generate_dataset(num_samples=args.samples)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"[+] Dataset successfully generated with {len(dataset)} samples.")
    print(f"[+] Saved to: {args.output}")

if __name__ == "__main__":
    main()
