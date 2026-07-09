from __future__ import annotations

import logging
import threading
from queue import Queue
from typing import Callable
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)


class VoskRecognizer:
    """A lightweight Vosk-based recognizer that reads from sounddevice if available.

    Behavior:
    - `available` property is True if both `vosk` and `sounddevice` are installed and a model path exists.
    - `start_listening()` spawns a background thread that streams audio and pushes transcriptions to `transcriptions` queue.
    - `stop_listening()` stops the background thread.

    NOTE: Models are not bundled. Set `VOSK_MODEL_PATH` env var to point to a downloaded Vosk model directory, or place a model under `./models/vosk-model`.
    """

    def __init__(self) -> None:
        self._loaded = False
        self.transcriptions: Queue[str] = Queue()
        self.state = "stopped"
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        # Lazy imports
        try:
            import vosk  # type: ignore
            import sounddevice as sd  # type: ignore
        except Exception as exc:  # noqa: BLE001 - we want to catch import errors here
            logger.debug("Vosk or sounddevice not available: %s", exc)
            self._vosk = None
            self._sd = None
            return

        self._vosk = vosk
        self._sd = sd

        # Determine model path
        model_path = os.environ.get("VOSK_MODEL_PATH")
        if model_path and os.path.isdir(model_path):
            self._model_path = model_path
        else:
            # Fallback to ./models/vosk-model
            candidate = os.path.join(os.getcwd(), "models", "vosk-model")
            if os.path.isdir(candidate):
                self._model_path = candidate
            else:
                self._model_path = None

        if self._model_path is None:
            logger.debug("Vosk model not found; set VOSK_MODEL_PATH or place model in ./models/vosk-model")
            return

        try:
            self._model = self._vosk.Model(self._model_path)
            self._loaded = True
        except Exception as exc:
            logger.exception("Failed to load Vosk model: %s", exc)
            self._loaded = False

    @property
    def available(self) -> bool:
        return bool(self._vosk and self._sd and self._loaded)

    def _audio_callback(self, indata, frames, time, status):
        # callback from sounddevice.Stream
        if status:
            logger.debug("Sounddevice status: %s", status)
        # `indata` may be a NumPy array or a cffi buffer; ensure bytes
        try:
            chunk = indata.tobytes()
        except Exception:
            chunk = bytes(indata)
        if not self._recog.AcceptWaveform(chunk):
            # partial result can be ignored or parsed
            pass
        else:
            res = self._recog.Result()
            # res is a JSON string, extract text
            try:
                import json

                j = json.loads(res)
                text = j.get("text", "").strip()
                if text:
                    logger.debug("Vosk transcription: %s", text)
                    self.transcriptions.put(text)
            except Exception:
                logger.exception("Failed to parse Vosk result")

    def start_listening(self) -> None:
        if not self.available:
            raise RuntimeError("Vosk recognizer unavailable: dependencies or model missing")
        if self.state == "listening":
            return

        self._stop_event.clear()
        self._recog = self._vosk.KaldiRecognizer(self._model, 16000)

        def run():
            try:
                with self._sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=self._audio_callback):
                    self.state = "listening"
                    logger.info("Vosk recognizer started listening")
                    while not self._stop_event.is_set():
                        self._sd.sleep(100)
            except Exception as exc:
                logger.exception("Vosk listening failed: %s", exc)
                self.state = "stopped"

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop_listening(self) -> None:
        if self._thread is None:
            return
        self._stop_event.set()
        self._thread.join(timeout=2.0)
        self._thread = None
        self.state = "stopped"
        logger.info("Vosk recognizer stopped")

    def get_transcription(self) -> str | None:
        if self.transcriptions.empty():
            return None
        return self.transcriptions.get_nowait()
