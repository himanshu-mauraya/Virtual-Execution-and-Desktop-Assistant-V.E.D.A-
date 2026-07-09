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
            "open_app": ["open", "launch", "start", "run"],
            "screenshot": ["screenshot", "screen shot", "capture screen", "take a screenshot"],
            "shutdown": ["shutdown", "turn off", "power off", "shut down"],
            "restart": ["restart", "reboot", "reload"],
            "lock": ["lock"],
            "sleep": ["sleep", "hibernate", "standby", "put to sleep", "go to sleep"],
            "search": ["search", "look up", "find", "google"],
        }
        self._targets = {
            "vscode": ["vscode", "visual studio code", "code editor", "code"],
            "browser": ["browser", "chrome", "google chrome", "brave", "firefox", "edge", "internet"],
            "calculator": ["calculator", "calc", "calculate"],
            "notepad": ["notepad", "text editor", "editor"],
            "spotify": ["spotify"],
            "explorer": ["file explorer", "explorer", "files", "file manager"],
        }

    def classify(self, text: str) -> Intent:
        normalized = text.lower().strip()
        if not normalized:
            return Intent(intent="unknown")

        # Match more specific non-open intents first to avoid accidental open_app matches.
        intent_priority = ["shutdown", "restart", "lock", "sleep", "search", "screenshot", "open_app"]
        for intent in intent_priority:
            keywords = self._patterns.get(intent, [])
            if any(keyword in normalized for keyword in keywords):
                if intent == "open_app":
                    target = self._extract_target(normalized)
                    return Intent(intent=intent, target=target, confidence=0.95 if target != "unknown" else 0.75)
                return Intent(intent=intent, confidence=0.9)

        return Intent(intent="unknown")

    def _extract_target(self, normalized: str) -> str:
        for target, aliases in self._targets.items():
            for alias in aliases:
                if alias in normalized:
                    return target
        return "unknown"
