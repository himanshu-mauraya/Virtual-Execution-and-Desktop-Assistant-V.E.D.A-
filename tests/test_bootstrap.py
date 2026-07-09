from unittest.mock import Mock

from src.veda_ai.bootstrap import AppContext, AppConfig, build_app_context, load_app_config


def test_load_app_config_defaults() -> None:
    config = load_app_config()
    assert config.ai_provider == "openai"
    assert config.log_level == "INFO"
    assert config.voice_enabled is True


def test_build_app_context() -> None:
    config = AppConfig(openai_api_key="test-key", voice_enabled=False)
    context = build_app_context(config, database_path=":memory:")
    assert isinstance(context, AppContext)
    assert context.config.openai_api_key == "test-key"
    assert context.speech_engine is None
    assert context.command_engine is not None
    assert context.database.get_setting("missing") is None


def test_build_app_context_falls_back_to_vosk_when_speech_recognizer_unavailable(monkeypatch) -> None:
    config = AppConfig(openai_api_key="test-key", voice_enabled=True, offline_mode=False)
    monkeypatch.setattr("src.veda_ai.bootstrap.SpeechRecognizer.available", property(lambda self: False))
    fake_vosk = Mock()
    fake_vosk.available = True
    monkeypatch.setattr("src.veda_ai.bootstrap.VoskRecognizer", lambda: fake_vosk)

    context = build_app_context(config, database_path=":memory:")
    assert context.recognizer is fake_vosk


def test_build_app_context_disables_unavailable_microphone(monkeypatch) -> None:
    config = AppConfig(openai_api_key="test-key", voice_enabled=True, offline_mode=False)
    monkeypatch.setattr("src.veda_ai.bootstrap.SpeechRecognizer.available", property(lambda self: False))
    fake_vosk = Mock()
    fake_vosk.available = False
    monkeypatch.setattr("src.veda_ai.bootstrap.VoskRecognizer", lambda: fake_vosk)

    context = build_app_context(config, database_path=":memory:")
    assert context.recognizer is None


def test_build_app_context_prefers_vosk_in_offline_mode(monkeypatch) -> None:
    config = AppConfig(openai_api_key="test-key", voice_enabled=True, offline_mode=True)
    fake_vosk = Mock()
    fake_vosk.available = True
    monkeypatch.setattr("src.veda_ai.bootstrap.VoskRecognizer", lambda: fake_vosk)

    context = build_app_context(config, database_path=":memory:")
    assert context.recognizer is fake_vosk


def test_build_app_context_falls_back_to_speech_when_vosk_unavailable(monkeypatch) -> None:
    config = AppConfig(openai_api_key="test-key", voice_enabled=True, offline_mode=True)
    fake_vosk = Mock()
    fake_vosk.available = False
    fake_speech = Mock()
    fake_speech.available = True
    monkeypatch.setattr("src.veda_ai.bootstrap.VoskRecognizer", lambda: fake_vosk)
    monkeypatch.setattr("src.veda_ai.bootstrap.SpeechRecognizer", lambda: fake_speech)

    context = build_app_context(config, database_path=":memory:")
    assert context.recognizer is fake_speech
