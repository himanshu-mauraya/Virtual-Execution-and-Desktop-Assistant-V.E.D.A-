from __future__ import annotations

import logging
from queue import Queue
from typing import Callable

import speech_recognition as sr

from .typing import VoiceState

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.microphone: sr.Microphone | None = None
        self.state = VoiceState.STOPPED
        self._stop_listening: Callable[[bool], None] | None = None
        self.transcriptions: Queue[str] = Queue()

    def _ensure_microphone(self) -> None:
        if self.microphone is not None:
            return

        try:
            self.microphone = sr.Microphone()
        except (OSError, AttributeError) as error:
            logger.exception("Microphone unavailable or PyAudio missing: %s", error)
            raise RuntimeError("Microphone unavailable or PyAudio missing") from error

    def start_listening(self) -> None:
        if self.state == VoiceState.LISTENING:
            return

        self._ensure_microphone()
        try:
            assert self.microphone is not None
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self._stop_listening = self.recognizer.listen_in_background(
                self.microphone, self._callback, phrase_time_limit=6
            )
            self.state = VoiceState.LISTENING
            logger.info("Speech recognizer started listening")
        except OSError as error:
            logger.exception("Speech recognizer failed to start: %s", error)
            raise RuntimeError("Speech recognizer failed to start") from error

    def stop_listening(self) -> None:
        if self._stop_listening is not None:
            self._stop_listening(wait_for_stop=False)
            self._stop_listening = None
        self.state = VoiceState.STOPPED
        logger.info("Speech recognizer stopped")

    def _callback(self, recognizer: sr.Recognizer, audio: sr.AudioData) -> None:
        try:
            transcript = recognizer.recognize_google(audio)
            logger.debug("Transcription received: %s", transcript)
            self.transcriptions.put(transcript)
        except sr.UnknownValueError:
            logger.debug("Speech was not understood")
        except sr.RequestError as error:
            logger.warning("Speech recognition request failed: %s", error)
            self.transcriptions.put("[voice recognition unavailable]")

    @property
    def available(self) -> bool:
        try:
            self._ensure_microphone()
            return True
        except RuntimeError:
            return False

    def get_transcription(self) -> str | None:
        if self.transcriptions.empty():
            return None

        return self.transcriptions.get_nowait()
