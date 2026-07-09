from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(slots=True)
class Intent:
    intent: str
    target: str | None = None
    confidence: float = 1.0


class CommandEngine:
    """Lightweight intent classifier for voice commands."""

    def __init__(self) -> None:
        self._patterns: Dict[str, List[str]] = {
            "open_app": ["open", "launch"],
            "screenshot": ["screenshot", "capture screen"],
            "shutdown": ["shutdown", "turn off"],
            "restart": ["restart", "reboot"],
            "lock": ["lock"],
            "sleep": ["sleep", "hibernate"],
            "search": ["search", "look up", "find"],
        }
        self._targets = {
            "vscode": ["vscode", "visual studio code", "code"],
            "chrome": ["chrome", "google chrome", "browser"],
            "calculator": ["calculator", "calc"],
            "notepad": ["notepad", "text editor"],
            "spotify": ["spotify"],
        }

    def classify(self, text: str) -> Intent:
        normalized = text.lower().strip()
        if not normalized:
            return Intent(intent="unknown")

        for intent, keywords in self._patterns.items():
            if any(keyword in normalized for keyword in keywords):
                if intent == "open_app":
                    for target, aliases in self._targets.items():
                        if any(alias in normalized for alias in aliases):
                            return Intent(intent=intent, target=target, confidence=0.95)
                    return Intent(intent=intent, target="unknown", confidence=0.8)
                return Intent(intent=intent, confidence=0.9)

        return Intent(intent="unknown")
