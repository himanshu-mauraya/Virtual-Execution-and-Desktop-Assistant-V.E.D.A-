from __future__ import annotations

import logging
import pyttsx3

from .typing import VoiceState


logger = logging.getLogger(__name__)


class SpeechEngine:
    """Simple TTS engine wrapper for VEDA AI."""

    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        self.state = VoiceState.STOPPED

    def speak(self, text: str) -> None:
        logger.debug("Speaking text: %s", text)
        self.state = VoiceState.SPEAKING
        self.engine.say(text)
        self.engine.runAndWait()
        self.state = VoiceState.STOPPED

    def stop(self) -> None:
        self.engine.stop()
        self.state = VoiceState.STOPPED
