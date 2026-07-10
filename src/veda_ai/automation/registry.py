from __future__ import annotations

import logging
import os
import shutil
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AppRegistry:
    """Discover and map common installed applications to launch commands.

    This is a lightweight heuristic registry: prefer `shutil.which` results,
    then probe common Program Files locations for known executables.
    """

    def __init__(self) -> None:
        self._map: Dict[str, str] = {}
        self._populate_defaults()

    def _populate_defaults(self) -> None:
        # Common app -> executable name candidates
        candidates = {
            "chrome": ["chrome.exe", "googlechrome.exe", "chrome"],
            "edge": ["msedge.exe", "msedge"],
            "firefox": ["firefox.exe", "firefox"],
            "brave": ["brave.exe", "brave"],
            "vscode": ["code.exe", "code"],
            "spotify": ["spotify.exe", "spotify"],
            "discord": ["discord.exe", "discord"],
            "whatsapp": ["WhatsApp.exe", "WhatsApp"] ,
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "explorer": ["explorer.exe"],
        }

        # Try which first
        for name, exes in candidates.items():
            for exe in exes:
                path = shutil.which(exe)
                if path:
                    self._map[name] = path
                    break

        # Probe Program Files if not found
        prog_roots = [os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")]
        prog_roots = [p for p in prog_roots if p]
        if prog_roots:
            for name, exes in candidates.items():
                if name in self._map:
                    continue
                for root in prog_roots:
                    for exe in exes:
                        candidate = os.path.join(root, exe)
                        if os.path.exists(candidate):
                            self._map[name] = candidate
                            break
                    if name in self._map:
                        break

    def register(self, name: str, path: str) -> None:
        self._map[name.lower()] = path

    def find(self, name: str) -> Optional[str]:
        if not name:
            return None
        key = name.lower().strip()
        # direct lookup
        if key in self._map:
            return self._map[key]

        # substring match
        for k, v in self._map.items():
            if k in key or key in k:
                return v

        # try which on the raw name
        path = shutil.which(key)
        if path:
            return path

        logger.debug("AppRegistry: no executable found for %s", name)
        return None
