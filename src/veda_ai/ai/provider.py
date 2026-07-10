from __future__ import annotations

from abc import ABC, abstractmethod
import json
import logging
import os
from typing import Any, Dict

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore


logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract AI provider interface."""

    @abstractmethod
    def send_prompt(self, prompt: str) -> str:
        raise NotImplementedError

    def send_structured(self, prompt: str) -> Dict[str, Any]:
        """Optional: request a structured JSON response from the provider.

        Providers may implement a best-effort JSON parser that extracts JSON
        embedded in the model output.
        """
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
        if OpenAI and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception:
                logger.exception("Failed to initialize OpenAI client")
                self.client = None
        else:
            self.client = None

    def send_prompt(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("OpenAI client is not available or API key missing.")

        try:
            # Use Responses API when available; fall back to stringification.
            resp = self.client.responses.create(model=self.model, input=prompt)
            # Try common properties for textual content
            text = None
            if hasattr(resp, "output_text") and resp.output_text:
                text = resp.output_text
            else:
                out = getattr(resp, "output", None)
                if out:
                    # out may be a list of dict-like objects
                    try:
                        first = out[0]
                        # Try common nested shapes
                        if isinstance(first, dict):
                            content = first.get("content") or first.get("message")
                            if isinstance(content, list) and content:
                                # find text-like piece
                                for item in content:
                                    if isinstance(item, dict) and item.get("type") in ("output_text", "message"):
                                        text = item.get("text") or item.get("content")
                                        break
                        # As last resort, stringify
                    except Exception:
                        pass

            if text is None:
                text = str(resp)

            return text
        except Exception:
            logger.exception("OpenAI request failed")
            raise

    def send_structured(self, prompt: str) -> Dict[str, Any]:
        text = self.send_prompt(prompt)
        # Try to parse JSON from the response text
        try:
            return json.loads(text)
        except Exception:
            # Try to extract a JSON substring
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = text[start : end + 1]
                try:
                    return json.loads(candidate)
                except Exception:
                    logger.exception("Failed to parse JSON candidate from AI response")
            raise RuntimeError("AI provider returned non-JSON response")


__all__ = ["AIProvider", "OpenAIProvider"]
