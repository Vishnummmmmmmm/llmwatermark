"""
slm_text_generator.py — Local Small Language Model (SLM) Text Generator & Paraphraser

Architecture:
- Utilizes Qwen/Qwen2.5-0.5B-Instruct (~490M params, ~400MB RAM/VRAM)
- Lazy-loaded singleton so detector startup remains instant (<0.1ms)
- Provides:
  1. rewrite_sentence(sentence): Neural paraphraser for clean, unwatermarked rewrites
  2. generate_text(prompt, max_tokens): Direct generation of clean text
"""
import torch
from typing import Optional
from transformers import AutoModelForCausalLM, AutoTokenizer

DEFAULT_SLM_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"

class SLMTextGenerator:
    """
    On-device Small Language Model (SLM) generator and neural rewriter.
    """
    def __init__(self, model_id: str = DEFAULT_SLM_MODEL_ID):
        self.model_id = model_id
        self.tokenizer = None
        self.model = None
        self._is_loaded = False

    def load_model(self):
        """
        Loads model weights on demand (lazy loading).
        """
        if self._is_loaded:
            return
        print(f"[*] Initializing local SLM ({self.model_id})...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        # Use torch.float32 or float16 based on availability
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        if not torch.cuda.is_available():
            self.model.to("cpu")
            
        self.model.eval()
        self._is_loaded = True
        print(f"[+] SLM successfully loaded on {device.upper()}.")

    def rewrite_sentence(self, sentence: str) -> str:
        """
        Neural paraphraser: Rewrites a sentence naturally to remove robotic or biased phrasing
        while strictly preserving factual meaning and tone.
        """
        self.load_model()
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert editorial writer. Rewrite the provided text naturally and fluently in standard English. "
                    "Preserve the exact meaning and facts. Do NOT add preamble, commentary, or quotes. Output ONLY the rewritten sentence."
                )
            },
            {"role": "user", "content": f"Rewrite: {sentence}"}
        ]
        
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer([formatted_prompt], return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
        with torch.no_grad():
            output_tokens = self.model.generate(
                **inputs,
                max_new_tokens=len(sentence.split()) + 35,
                temperature=0.3,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
        prompt_len = inputs["input_ids"].shape[1]
        generated_tokens = output_tokens[0][prompt_len:]
        rewritten = self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        # Strip surrounding quotes if present
        if (rewritten.startswith('"') and rewritten.endswith('"')) or (rewritten.startswith("'") and rewritten.endswith("'")):
            rewritten = rewritten[1:-1].strip()
            
        return rewritten

    def generate_text(self, prompt: str, max_tokens: int = 150) -> str:
        """
        Generates fresh, unwatermarked text based on a user prompt.
        """
        self.load_model()
        
        messages = [
            {
                "role": "system",
                "content": "You are a concise, helpful, and natural AI assistant. Write clear and informative responses."
            },
            {"role": "user", "content": prompt}
        ]
        
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer([formatted_prompt], return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
        with torch.no_grad():
            output_tokens = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
        prompt_len = inputs["input_ids"].shape[1]
        generated_tokens = output_tokens[0][prompt_len:]
        return self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

# Global singleton (lazy-loaded)
_global_slm_instance: Optional[SLMTextGenerator] = None

def get_slm_generator() -> SLMTextGenerator:
    global _global_slm_instance
    if _global_slm_instance is None:
        _global_slm_instance = SLMTextGenerator()
    return _global_slm_instance
