"""
Base Agent class for AgriPlan AI multi-agent architecture.
Provides unified prompt formatting and model execution interface.
"""

from models.llm_factory import LLMProvider, DEFAULT_FAST_MODEL, DEFAULT_REASONING_MODEL

class BaseAgent:
    def __init__(self, name: str, role: str, model_type: str = "reasoning", api_key: str = None):
        self.name = name
        self.role = role
        self.provider = LLMProvider(api_key=api_key)
        self.model = DEFAULT_FAST_MODEL if model_type == "fast" else DEFAULT_REASONING_MODEL

    def execute(self, prompt: str, system_prompt: str = "") -> str:
        sys = system_prompt or f"You are {self.name}, an expert AI agent specialized as: {self.role}."
        return self.provider.generate(prompt=prompt, system_prompt=sys, model=self.model)
