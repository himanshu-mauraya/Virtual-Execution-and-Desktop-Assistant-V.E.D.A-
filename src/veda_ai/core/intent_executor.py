from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from typing import Callable

from .command_engine import Intent
from .intent_parser import IntentAction
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

    def execute_actions(
        self,
        actions: list[IntentAction],
        raw_text: str,
        automation: AutomationController,
        system: SystemManager,
    ) -> IntentResponse:
        if not actions:
            logger.warning("No intent actions found for text: %s", raw_text)
            return IntentResponse(False, "I couldn't understand that command.", action="unknown")

        messages: list[str] = []
        succeeded_any = False

        for action in actions:
            handler = self._get_handler(action.intent)
            if handler is None:
                messages.append(f"Intent '{action.intent}' is not supported yet.")
                continue

            try:
                handler(action.parameters or {}, automation, system)
                messages.append(self._success_message(action))
                succeeded_any = True
            except Exception as exc:
                logger.exception("Action %s failed", action.intent)
                messages.append(f"Failed to execute {action.intent}: {exc}")

        if not succeeded_any:
            return IntentResponse(False, " ".join(messages).strip() or "I couldn't execute any actions.", action="batch")

        return IntentResponse(True, " ".join(messages).strip(), action="batch")

    def _get_handler(self, intent: str) -> Callable[[dict[str, object], AutomationController, SystemManager], None] | None:
        return {
            "open_application": self._open_application,
            "browser_search": self._browser_search,
            "google_search": self._google_search,
            "youtube_search": self._youtube_search,
            "open_website": self._open_website,
            "open_folder": self._open_folder,
            "take_screenshot": self._take_screenshot,
            "volume": self._set_volume,
            "brightness": self._set_brightness,
            "mute": self._mute,
            "unmute": self._unmute,
            "shutdown": self._shutdown,
            "restart": self._restart,
            "lock_pc": self._lock_pc,
            "sleep": self._sleep,
        }.get(intent)

    def _success_message(self, action: IntentAction) -> str:
        if action.intent == "open_application":
            application = action.parameters.get("application", "application")
            return f"Opening {application}."
        if action.intent == "open_website":
            return "Opening website."
        if action.intent == "google_search":
            return "Searching Google."
        if action.intent == "youtube_search":
            return "Searching YouTube."
        if action.intent == "browser_search":
            return "Searching the web."
        if action.intent == "open_folder":
            folder = action.parameters.get("folder", "folder")
            return f"Opening {folder}."
        if action.intent == "take_screenshot":
            return "Screenshot has been taken."
        if action.intent == "volume":
            if "direction" in action.parameters:
                return f"Volume {action.parameters['direction']}."
            return "Adjusting volume."
        if action.intent == "brightness":
            return "Adjusting brightness."
        if action.intent == "mute":
            return "Muting volume."
        if action.intent == "unmute":
            return "Unmuting volume."
        if action.intent == "shutdown":
            return "Shutting down the PC."
        if action.intent == "restart":
            return "Restarting the PC."
        if action.intent == "lock_pc":
            return "Locking the PC."
        if action.intent == "sleep":
            return "Putting the PC to sleep."
        return f"Executed {action.intent}."

    def _open_application(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        application = str(parameters.get("application", ""))
        automation.open_application(application)

    def _browser_search(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        query = str(parameters.get("query", ""))
        automation.search_web(query)

    def _google_search(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        query = str(parameters.get("query", ""))
        automation.google_search(query)

    def _youtube_search(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        query = str(parameters.get("query", ""))
        automation.youtube_search(query)

    def _open_website(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        url = str(parameters.get("url", ""))
        automation.open_website(url)

    def _open_folder(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        folder = str(parameters.get("folder", ""))
        automation.open_folder(folder)

    def _take_screenshot(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        automation.take_screenshot("veda_screenshot.png")

    def _set_volume(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        direction = str(parameters.get("direction", "toggle"))
        level = parameters.get("level")
        automation.set_volume(direction=direction, level=level)

    def _set_brightness(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        level = int(parameters.get("level", 0)) if parameters.get("level") is not None else None
        if level is not None:
            automation.set_brightness(level)
        else:
            automation.set_brightness(50)

    def _mute(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        automation.mute()

    def _unmute(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        automation.unmute()

    def _shutdown(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        system.shutdown()

    def _restart(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        system.restart()

    def _lock_pc(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        system.lock()

    def _sleep(self, parameters: dict[str, object], automation: AutomationController, system: SystemManager) -> None:
        system.sleep()
