"""
Layer B Paraphraser Engine
Orchestrates deep statistical paraphrasing using local Ollama models (e.g., llama3.2, deepseek)
with offline syntactic restructuring fallback.
"""
import urllib.request
import urllib.error
import json
import re

class LayerBParaphraser:
    @staticmethod
    def paraphrase_text(text: str, model_name: str = "llama3.2") -> tuple[str, bool]:
        """
        Executes a Layer B rewrite pass via local Ollama endpoint (http://127.0.0.1:11434/api/generate).
        Returns (rewritten_text, used_ollama_flag).
        """
        prompt = f"Paraphrase the following text into natural, human writing. Retain all original facts and details. Do not add intro/outro commentary, only return the rewritten text:\n\n{text}"
        
        try:
            req_data = json.dumps({
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }).encode('utf-8')

            req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=req_data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    resp_json = json.loads(response.read().decode('utf-8'))
                    response_text = resp_json.get("response", "").strip()
                    if response_text:
                        return response_text, True
        except Exception:
            pass

        # Offline Layer B Syntactic Restructuring Fallback
        sentences = re.split(r'(?<=[.!?]) +', text)
        rewritten = []
        for sent in sentences:
            if " and " in sent and len(sent) > 60:
                parts = sent.split(" and ", 1)
                rewritten.append(f"{parts[0]}. Additionally, {parts[1]}")
            elif " because " in sent:
                parts = sent.split(" because ", 1)
                rewritten.append(f"Since {parts[1].rstrip('.')}, {parts[0]}")
            else:
                rewritten.append(sent)

        return " ".join(rewritten), False
