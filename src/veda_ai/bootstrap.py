from __future__ import annotations

import logging
from dataclasses import dataclass

from dotenv import load_dotenv

from .ai.provider import AIProvider, OpenAIProvider
from .automation.controller import AutomationController
from .automation.registry import AppRegistry
from .config.settings import AppConfig
from .core.command_engine import CommandEngine
from .core.intent_executor import IntentExecutor
from .core.intent_parser import IntentParser
from .database.manager import DatabaseManager
from .system.manager import SystemManager
from .voice.recognizer import SpeechRecognizer
from .voice.vosk_recognizer import VoskRecognizer
from .voice.speech_engine import SpeechEngine


@dataclass(slots=True)
class AppContext:
    config: AppConfig
    database: DatabaseManager
    ai_provider: AIProvider
    command_engine: CommandEngine
    intent_parser: IntentParser
    intent_executor: IntentExecutor
    automation: AutomationController
    app_registry: "AppRegistry"
    system: SystemManager
    speech_engine: SpeechEngine | None = None
    recognizer: SpeechRecognizer | None = None


def setup_logging(log_level: str = "INFO") -> None:
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def load_app_config() -> AppConfig:
    load_dotenv()
    config = AppConfig()
    setup_logging(config.log_level)
    logging.getLogger(__name__).debug("Loaded app config: %s", config)
    return config


def build_app_context(config: AppConfig, database_path: str | None = None) -> AppContext:
    database = DatabaseManager(database_path or "veda_ai.db")
    ai_provider = OpenAIProvider(config.openai_api_key)
    command_engine = CommandEngine()
    intent_parser = IntentParser()
    intent_executor = IntentExecutor()
    app_registry = AppRegistry()
    automation = AutomationController(app_registry=app_registry)
    system = SystemManager()
    speech_engine = SpeechEngine() if config.voice_enabled else None
    recognizer: SpeechRecognizer | None = None

    if config.voice_enabled:
        # Prefer offline Vosk recognizer when offline_mode is requested
        recognizer: SpeechRecognizer | VoskRecognizer | None
        if config.offline_mode:
            vosk_recog = VoskRecognizer()
            if vosk_recog.available:
                recognizer = vosk_recog
            else:
                logging.getLogger(__name__).warning("Vosk offline recognizer unavailable; falling back to SpeechRecognizer")
                sr = SpeechRecognizer()
                recognizer = sr if sr.available else None
        else:
            sr = SpeechRecognizer()
            if sr.available:
                recognizer = sr
            else:
                # Try vosk as fallback
                vosk_recog = VoskRecognizer()
                if vosk_recog.available:
                    recognizer = vosk_recog
                else:
                    logging.getLogger(__name__).warning("Voice recognizer disabled: microphone unavailable")
                    recognizer = None

    return AppContext(
        config=config,
        database=database,
        ai_provider=ai_provider,
        command_engine=command_engine,
        intent_parser=intent_parser,
        intent_executor=intent_executor,
        automation=automation,
        app_registry=app_registry,
        system=system,
        speech_engine=speech_engine,
        recognizer=recognizer,
    )
