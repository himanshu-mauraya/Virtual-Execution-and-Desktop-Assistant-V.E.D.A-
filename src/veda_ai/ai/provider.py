from __future__ import annotations

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstract AI provider interface."""

    @abstractmethod
    def send_prompt(self, prompt: str) -> str:
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def send_prompt(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("OpenAI API key is not configured.")
        return f"[openai] {prompt}"
