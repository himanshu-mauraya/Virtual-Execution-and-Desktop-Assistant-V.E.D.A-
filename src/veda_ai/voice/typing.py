from __future__ import annotations

from enum import Enum


class VoiceState(str, Enum):
    SPEAKING = "speaking"
    STOPPED = "stopped"
    LISTENING = "listening"
