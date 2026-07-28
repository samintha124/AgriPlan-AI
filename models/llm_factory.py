"""
Model Factory module for AgriPlan AI.
Handles multi-model selection (Groq / OpenRouter) satisfying the assignment requirement
to justify and use at least 2 distinct models (Fast router vs. Powerful reasoning model).
"""

import os
import json
import urllib.request
import urllib.error
from utils.config import get_api_key

# Default Model Specifications
DEFAULT_FAST_MODEL = "llama-3.1-8b-instant"       # Ultra fast routing & intent parsing
DEFAULT_REASONING_MODEL = "llama-3.3-70b-versatile" # Deep reasoning & detailed advice

class LLMProvider:
    def __init__(self, api_key: str = None, provider: str = "groq"):
        self.provider = provider.lower()
        self.api_key = api_key or get_api_key("GROQ_API_KEY") or get_api_key("OPENROUTER_API_KEY")
    
    def generate(self, prompt: str, system_prompt: str = "", model: str = None, temperature: float = 0.2) -> str:
        """
        Generate completions from Groq or OpenRouter via lightweight HTTP requests.
        """
        if not self.api_key:
            return "[Error: API Key missing. Please set GROQ_API_KEY or OPENROUTER_API_KEY in .env or Streamlit Secrets.]"

        if "openrouter" in self.provider or self.api_key.startswith("sk-or-"):
            return self._call_openrouter(prompt, system_prompt, model or "meta-llama/llama-3.3-70b-instruct", temperature)
        else:
            return self._call_groq(prompt, system_prompt, model or DEFAULT_REASONING_MODEL, temperature)

    def _call_groq(self, prompt: str, system_prompt: str, model: str, temperature: float) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2048
        }
        
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            return f"[Groq API Error {e.code}: {err_body}]"
        except Exception as e:
            return f"[Error connecting to Groq API: {str(e)}]"

    def _call_openrouter(self, prompt: str, system_prompt: str, model: str, temperature: float) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://streamlit.io",
            "X-Title": "AgriPlan AI",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2048
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[OpenRouter API Error: {str(e)}]"
