from unittest.mock import Mock, patch

import pytest

from src.veda_ai.voice.recognizer import SpeechRecognizer


def test_speech_recognizer_available_checks_microphone() -> None:
    with patch("src.veda_ai.voice.recognizer.sr.Microphone") as mock_microphone:
        recognizer = SpeechRecognizer()
        assert recognizer.available is True
        mock_microphone.assert_called_once()


def test_speech_recognizer_unavailable_when_microphone_errors() -> None:
    with patch("src.veda_ai.voice.recognizer.sr.Microphone", side_effect=OSError("No device")):
        recognizer = SpeechRecognizer()
        assert recognizer.available is False


def test_speech_recognizer_start_listening_raises_without_microphone() -> None:
    recognizer = SpeechRecognizer()
    with patch.object(recognizer, "_ensure_microphone", side_effect=RuntimeError("Microphone unavailable")):
        with pytest.raises(RuntimeError, match="Microphone unavailable"):
            recognizer.start_listening()
