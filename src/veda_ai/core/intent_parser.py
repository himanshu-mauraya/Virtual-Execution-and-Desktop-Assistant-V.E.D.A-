from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class IntentAction:
    intent: str
    parameters: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.parameters is None:
            self.parameters = {}

    def to_dict(self) -> dict[str, Any]:
        return {"intent": self.intent, **self.parameters}


@dataclass(slots=True)
class IntentParseResult:
    actions: list[IntentAction]
    raw_text: str

    def to_json(self) -> str:
        return json.dumps(
            {"actions": [action.to_dict() for action in self.actions]},
            ensure_ascii=False,
        )


class IntentParser:
    def __init__(self) -> None:
        self._connectors = re.compile(r"\b(?:then|phir|aur)\b", re.IGNORECASE)
        self._website_map = {
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "gmail": "https://mail.google.com",
            "chatgpt": "https://chat.openai.com",
            "github": "https://github.com",
            "hdhub": "https://hdhub.org",
            "animepahe": "https://animepahe.com",
            "linkedin": "https://www.linkedin.com",
            "netflix": "https://www.netflix.com",
            "youtube": "https://www.youtube.com",
            "spotify": "https://open.spotify.com",
        }
        self._app_aliases = {
            "chrome": ["chrome", "google chrome"],
            "edge": ["edge", "microsoft edge"],
            "firefox": ["firefox"],
            "browser": ["browser", "internet browser"],
            "vscode": ["vscode", "visual studio code", "code editor", "code"],
            "spotify": ["spotify"],
            "discord": ["discord"],
            "whatsapp": ["whatsapp", "whats app"],
            "notepad": ["notepad", "text editor", "editor"],
            "calculator": ["calculator", "calc"],
            "explorer": ["explorer", "file explorer", "files", "file manager"],
            "photoshop": ["photoshop", "photo shop"],
            "terminal": ["terminal", "powershell", "command prompt", "cmd"],
            "code": ["code"],
        }
        self._open_triggers = ["open", "launch", "start", "run", "khol", "kholna", "chalu"]
        self._search_terms = ["search", "find", "google", "dhundo", "dhund" ]
        self._youtube_terms = ["youtube", "yt", "songs", "play", "chala", "video", "music"]
        self._screenshot_terms = ["screenshot", "screen shot", "capture screen", "take a screenshot", "screenshot le"]
        self._mute_terms = ["mute", "volume off", "chup", "khamosh"]
        self._unmute_terms = ["unmute", "volume on", "sound on"]
        self._brightness_terms = ["brightness", "bright", "roshni"]
        self._volume_terms = ["volume", "aawaz", "sound", "thoda kam", "thoda zyada"]
        self._folder_terms = ["folder", "downloads", "desktop", "documents", "documents", "pictures", "downloads folder"]
        # custom folder aliases
        self._custom_folders = {
            "genshin": r"C:\\Program Files\\Genshin Impact",
            "genshin impact": r"C:\\Program Files\\Genshin Impact",
        }

    def parse(self, text: str) -> IntentParseResult:
        normalized = text.strip()
        if not normalized:
            return IntentParseResult([], text)

        segments = self._split_segments(normalized)
        actions: list[IntentAction] = []
        for segment in segments:
            action = self._parse_segment(segment)
            if action is not None:
                actions.append(action)

        return IntentParseResult(actions, text)

    def parse_with_ai(self, text: str, ai_provider) -> IntentParseResult:
        """Ask an AI provider (Gemini/OpenAI) to return structured actions JSON.

        The provider must implement `send_structured(prompt)` which returns a
        Python dict with an `actions` list, where each action is an object
        with an `intent` string and optional parameters.
        """
        if ai_provider is None:
            return IntentParseResult([], text)

        prompt = (
            "You are an intent parser for a desktop automation assistant. "
            "Return a JSON object with a single `actions` array. Each action must be an object with an `intent` string from the supported intents list and any parameters needed. "
            "The user utterance is:\n\n" + text + "\n\n" +
            "Supported intents: open_application, close_application, browser_search, google_search, youtube_search, open_website, search_file, open_folder, create_folder, delete_file, rename_file, copy_file, move_file, compress_file, extract_zip, shutdown, restart, lock_pc, sleep, volume, brightness, mute, unmute, take_screenshot, screen_record, weather, news, music, play_song, pause_music, next_song, previous_song, whatsapp, email, calendar, reminder, timer, alarm, clipboard, ocr, translate, summarize, chat, system_info, battery, cpu, memory, disk, internet_speed. "
            "Return only valid JSON. Example: {\"actions\":[{\"intent\":\"open_application\",\"application\":\"chrome\"}]}"
        )

        try:
            response = ai_provider.send_structured(prompt)
            if not isinstance(response, dict):
                return IntentParseResult([], text)
            actions = []
            for a in response.get("actions", []):
                if not isinstance(a, dict):
                    continue
                intent = a.get("intent")
                params = {k: v for k, v in a.items() if k != "intent"}
                if intent:
                    actions.append(IntentAction(intent=intent, parameters=params))

            return IntentParseResult(actions, text)
        except Exception:
            return IntentParseResult([], text)

    def _split_segments(self, text: str) -> list[str]:
        parts = [part.strip() for part in self._connectors.split(text) if part.strip()]
        return parts or [text.strip()]

    def _parse_segment(self, segment: str) -> IntentAction | None:
        normalized = segment.lower().strip()
        if not normalized:
            return None

        if self._matches_any(normalized, self._screenshot_terms):
            return IntentAction("take_screenshot")

        if self._matches_any(normalized, self._mute_terms):
            return IntentAction("mute")

        if self._matches_any(normalized, self._unmute_terms):
            return IntentAction("unmute")

        brightness_level = self._extract_level(normalized)
        if any(term in normalized for term in self._brightness_terms) and brightness_level is not None:
            return IntentAction("brightness", {"level": brightness_level})

        if self._matches_any(normalized, self._volume_terms):
            if "down" in normalized or "kam" in normalized or "minus" in normalized:
                return IntentAction("volume", {"direction": "down"})
            if "up" in normalized or "zyada" in normalized or "plus" in normalized:
                return IntentAction("volume", {"direction": "up"})
            if brightness_level is not None:
                return IntentAction("volume", {"level": brightness_level})
            return IntentAction("volume", {"direction": "toggle"})

        if any(term in normalized for term in ["shutdown", "shut down", "band karo", "power off", "turn off"]):
            return IntentAction("shutdown")

        if any(term in normalized for term in ["restart", "reboot", "restart karo", "dobara shuru"]):
            return IntentAction("restart")

        if any(term in normalized for term in ["lock", "lock pc", "lock computer", "lock karo"]):
            return IntentAction("lock_pc")

        if any(term in normalized for term in ["sleep", "hibernate", "suspend", "sleep karo"]):
            return IntentAction("sleep")

        folder = self._match_folder(normalized)
        if folder is not None:
            return IntentAction("open_folder", {"folder": folder})

        website = self._match_website(normalized)
        if website is not None:
            return IntentAction("open_website", {"url": website})

        if self._is_youtube_search(normalized):
            query = self._extract_search_query(normalized, ignore_terms=["youtube", "pe", "on"])
            return IntentAction("youtube_search", {"query": query or normalized})

        if self._is_google_search(normalized):
            query = self._extract_search_query(normalized, ignore_terms=["google", "pe", "on"])
            if query:
                return IntentAction("google_search", {"query": query})

        app_name = self._match_application(normalized)
        if app_name is not None:
            return IntentAction("open_application", {"application": app_name})

        if any(keyword in normalized for keyword in self._search_terms):
            return IntentAction("browser_search", {"query": normalized})

        if any(keyword in normalized for keyword in self._open_triggers):
            return IntentAction("open_application", {"application": normalized})

        return IntentAction("browser_search", {"query": normalized})

    def _matches_any(self, text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)

    def _extract_level(self, text: str) -> int | None:
        match = re.search(r"(\d{1,3})\s*%?", text)
        if match:
            level = int(match.group(1))
            return max(0, min(100, level))
        return None

    def _match_application(self, text: str) -> str | None:
        for name, aliases in self._app_aliases.items():
            if any(alias in text for alias in aliases):
                return name
        return None

    def _match_website(self, text: str) -> str | None:
        for alias, url in self._website_map.items():
            if alias in text:
                if self._is_open_phrase(text) or text.strip() == alias:
                    return url
        return None

    def _is_open_phrase(self, text: str) -> bool:
        return any(trigger in text for trigger in self._open_triggers) or any(
            keyword in text for keyword in ["khol", "kholna", "khelo", "launch"]
        )

    def _match_folder(self, text: str) -> str | None:
        for folder in self._folder_terms:
            if folder in text:
                if "download" in folder:
                    return "downloads"
                if "desktop" in folder:
                    return "desktop"
                if "document" in folder:
                    return "documents"
                if "picture" in folder:
                    return "pictures"
                return folder
        # check custom folder aliases
        for alias, path in self._custom_folders.items():
            if alias in text:
                return path
        return None

    def _is_google_search(self, text: str) -> bool:
        return any(term in text for term in ["google", "search", "find", "search karo", "dhundo"]) and "website" not in text

    def _is_youtube_search(self, text: str) -> bool:
        if any(term in text for term in ["open youtube", "youtube kholo", "open yt", "open youtube"]):
            return False
        return "youtube" in text or any(term in text for term in ["play", "song", "songs", "music", "chala"])

    def _extract_search_query(self, text: str, ignore_terms: list[str] | None = None) -> str:
        cleaned = text
        for term in (ignore_terms or []):
            cleaned = re.sub(rf"\b{re.escape(term)}\b", " ", cleaned)
        cleaned = re.sub(r"\b(open|search|google|pe|karo|khol|kholna|please|do|chala|play|khelo|karo|de)\b", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if cleaned.lower() in ("", "youtube", "google"):
            return text.strip()
        return cleaned
