from __future__ import annotations

import logging
from dataclasses import dataclass

from .command_engine import Intent
from ..automation.controller import AutomationController
from ..system.manager import SystemManager

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class IntentResponse:
    success: bool
    message: str
    action: str | None = None


class IntentExecutor:
    def execute_intent(
        self,
        intent: Intent,
        raw_text: str,
        automation: AutomationController,
        system: SystemManager,
    ) -> IntentResponse:
        logger.info("Executing intent %s for text: %s", intent.intent, raw_text)

        if intent.intent == "open_app":
            automation.open_application(raw_text)
            target = intent.target or "application"
            return IntentResponse(True, f"Opening {target}...", action="open_app")

        if intent.intent == "screenshot":
            automation.take_screenshot("veda_screenshot.png")
            return IntentResponse(True, "Screenshot captured to veda_screenshot.png.", action="screenshot")

        if intent.intent == "shutdown":
            system.shutdown()
            return IntentResponse(True, "System shutdown initiated.", action="shutdown")

        if intent.intent == "search":
            query = raw_text
            automation.search_web(query)
            return IntentResponse(True, f"Searching the web for '{query}'.", action="search")

        return IntentResponse(False, "I couldn't understand that command.", action="unknown")
