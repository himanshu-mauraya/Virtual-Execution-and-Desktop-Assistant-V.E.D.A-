from __future__ import annotations

import logging
import time
import webbrowser
from urllib.parse import quote_plus

import pyautogui

logger = logging.getLogger(__name__)


class AutomationController:
    """Basic automation wrapper for desktop actions."""

    def take_screenshot(self, path: str) -> None:
        logger.info("Taking screenshot to %s", path)
        screenshot = pyautogui.screenshot()
        screenshot.save(path)

    def open_application(self, command: str) -> None:
        logger.info("Requested automation open application: %s", command)
        normalized = command.lower()
        if "chrome" in normalized or "browser" in normalized:
            webbrowser.open("https://www.google.com")
        elif "vscode" in normalized or "code" in normalized:
            pyautogui.hotkey("win", "r")
            time.sleep(0.25)
            pyautogui.write("code\n")
        elif "notepad" in normalized:
            pyautogui.hotkey("win", "r")
            time.sleep(0.25)
            pyautogui.write("notepad\n")
        elif "calculator" in normalized or "calc" in normalized:
            pyautogui.hotkey("win", "r")
            time.sleep(0.25)
            pyautogui.write("calc\n")
        else:
            logger.warning("No automation rule for application command: %s", command)

    def search_web(self, query: str) -> None:
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        logger.info("Opening search URL: %s", url)
        webbrowser.open(url)
