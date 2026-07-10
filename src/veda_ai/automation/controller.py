from __future__ import annotations

import logging
import os
import subprocess
import time
import webbrowser
from urllib.parse import quote_plus

import pyautogui

logger = logging.getLogger(__name__)


class AutomationController:
    """Basic automation wrapper for desktop actions."""

    def __init__(self, app_registry=None) -> None:
        self._app_registry = app_registry

    def take_screenshot(self, path: str) -> None:
        logger.info("Taking screenshot to %s", path)
        screenshot = pyautogui.screenshot()
        screenshot.save(path)

    def open_application(self, command: str) -> None:
        logger.info("Requested automation open application: %s", command)
        normalized = command.lower()

        # If we have a registry, try to resolve an executable
        if self._app_registry is not None:
            exe = self._app_registry.find(normalized)
            if exe:
                try:
                    subprocess.Popen([exe])
                    return
                except Exception:
                    logger.exception("Failed to launch registry-resolved executable: %s", exe)

        if any(keyword in normalized for keyword in ("brave", "edge", "chrome", "firefox", "browser", "internet")):
            self._open_browser(normalized)
        elif any(keyword in normalized for keyword in ("vscode", "visual studio code", "code editor", "code")):
            self._open_vscode()
        elif any(keyword in normalized for keyword in ("notepad", "text editor", "editor")):
            self._open_notepad()
        elif any(keyword in normalized for keyword in ("calculator", "calc", "calculate")):
            self._open_calculator()
        elif any(keyword in normalized for keyword in ("file explorer", "explorer", "files", "file manager")):
            self._open_explorer()
        elif "spotify" in normalized:
            self._open_spotify()
        else:
            logger.warning("No automation rule for application command: %s", command)

    def _open_browser(self, normalized: str) -> None:
        logger.info("Opening browser for command: %s", normalized)
        if "brave" in normalized:
            try:
                subprocess.Popen(["brave"])
                return
            except Exception:
                pass
        if "edge" in normalized or "microsoft edge" in normalized:
            try:
                subprocess.Popen(["msedge"])
                return
            except Exception:
                pass
        if "firefox" in normalized:
            try:
                subprocess.Popen(["firefox"])
                return
            except Exception:
                pass
        if "chrome" in normalized or "google chrome" in normalized:
            try:
                subprocess.Popen(["chrome"])
                return
            except Exception:
                pass
        webbrowser.open("https://www.google.com")

    def _open_vscode(self) -> None:
        try:
            subprocess.Popen(["code"])
        except Exception:
            pyautogui.hotkey("win", "r")
            time.sleep(0.25)
            pyautogui.write("code\n")

    def _open_notepad(self) -> None:
        try:
            subprocess.Popen(["notepad.exe"])
        except Exception:
            pyautogui.hotkey("win", "r")
            time.sleep(0.25)
            pyautogui.write("notepad\n")

    def _open_calculator(self) -> None:
        try:
            subprocess.Popen(["calc.exe"])
        except Exception:
            pyautogui.hotkey("win", "r")
            time.sleep(0.25)
            pyautogui.write("calc\n")

    def _open_explorer(self) -> None:
        try:
            os.startfile("explorer")
        except Exception:
            try:
                subprocess.Popen(["explorer"])
            except Exception:
                webbrowser.open("file:///C:/")

    def _open_spotify(self) -> None:
        try:
            subprocess.Popen(["spotify"])
        except Exception:
            try:
                subprocess.Popen(["spotify.exe"])
            except Exception:
                webbrowser.open("https://open.spotify.com")

    def open_folder(self, folder: str) -> None:
        logger.info("Opening folder: %s", folder)
        paths = {
            "downloads": os.path.expanduser("~/Downloads"),
            "desktop": os.path.expanduser("~/Desktop"),
            "documents": os.path.expanduser("~/Documents"),
            "pictures": os.path.expanduser("~/Pictures"),
        }
        path = paths.get(folder.lower(), folder)
        try:
            os.startfile(path)
        except Exception:
            try:
                subprocess.Popen(["explorer", path])
            except Exception:
                webbrowser.open("file:///C:/")

    def open_website(self, url: str) -> None:
        logger.info("Opening website: %s", url)
        webbrowser.open(url)

    def google_search(self, query: str) -> None:
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        logger.info("Opening Google search URL: %s", url)
        webbrowser.open(url)

    def youtube_search(self, query: str) -> None:
        url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        logger.info("Opening YouTube search URL: %s", url)
        webbrowser.open(url)

    def set_volume(self, direction: str = "toggle", level: int | None = None) -> None:
        logger.info("Setting volume direction=%s level=%s", direction, level)
        if level is not None:
            pyautogui.press("volumedown" if level < 50 else "volumeup")
            return
        if direction == "down":
            pyautogui.press("volumedown")
        elif direction == "up":
            pyautogui.press("volumeup")
        else:
            pyautogui.press("volumemute")

    def set_brightness(self, level: int) -> None:
        logger.info("Setting brightness to %s", level)
        try:
            subprocess.run(["powershell", "-Command", f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"], check=False)
        except Exception:
            logger.warning("Brightness control not available on this system")

    def mute(self) -> None:
        logger.info("Muting system audio")
        # Toggle mute via OS-level press; actual confirmation will be handled by UI flow
        pyautogui.press("volumemute")

    def unmute(self) -> None:
        logger.info("Unmuting system audio")
        pyautogui.press("volumemute")

    def search_web(self, query: str) -> None:
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        logger.info("Opening search URL: %s", url)
        webbrowser.open(url)
