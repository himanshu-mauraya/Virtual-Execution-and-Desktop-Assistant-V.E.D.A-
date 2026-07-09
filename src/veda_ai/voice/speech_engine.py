from __future__ import annotations

import logging
import threading
import pyttsx3

from .typing import VoiceState


logger = logging.getLogger(__name__)


class SpeechEngine:
    """Simple TTS engine wrapper for VEDA AI.

    This class serializes speech requests with a lock so that
    `pyttsx3.Engine.runAndWait()` is not invoked concurrently from
    multiple threads which causes runtime errors.
    """

    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        self.state = VoiceState.STOPPED
        self._lock = threading.Lock()

    def speak(self, text: str) -> None:
        logger.debug("Speaking text: %s", text)
        # Serialize TTS calls to avoid pyttsx3 run-loop conflicts
        with self._lock:
            try:
                self.state = VoiceState.SPEAKING
                self.engine.say(text)
                self.engine.runAndWait()
            finally:
                self.state = VoiceState.STOPPED

    def stop(self) -> None:
        try:
            with self._lock:
                self.engine.stop()
        finally:
            self.state = VoiceState.STOPPED
