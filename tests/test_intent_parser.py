from unittest.mock import Mock

from src.veda_ai.core.intent_parser import IntentParser
from src.veda_ai.core.intent_executor import IntentExecutor
from src.veda_ai.automation.controller import AutomationController
from src.veda_ai.system.manager import SystemManager


def test_intent_parser_parses_multi_action_command() -> None:
    parser = IntentParser()
    result = parser.parse("Open Chrome then search Python tutorial then open ChatGPT")

    assert len(result.actions) == 3
    assert result.actions[0].intent == "open_application"
    assert result.actions[1].intent == "google_search"
    assert result.actions[1].parameters["query"] == "python tutorial"
    assert result.actions[2].intent == "open_website"
    assert result.actions[2].parameters["url"] == "https://chat.openai.com"


def test_intent_parser_parses_hinglish_open_command() -> None:
    parser = IntentParser()
    result = parser.parse("Chrome kholo")

    assert len(result.actions) == 1
    assert result.actions[0].intent == "open_application"
    assert result.actions[0].parameters["application"] == "chrome"


def test_intent_parser_parses_youtube_search() -> None:
    parser = IntentParser()
    result = parser.parse("YouTube pe Arijit Singh songs chala do")

    assert len(result.actions) == 1
    assert result.actions[0].intent == "youtube_search"
    assert "arijit singh songs" in result.actions[0].parameters["query"]


def test_intent_executor_executes_google_search() -> None:
    executor = IntentExecutor()
    automation = AutomationController()
    system = SystemManager()
    automation.google_search = Mock()

    result = executor.execute_actions(
        [
            type("A", (), {"intent": "google_search", "parameters": {"query": "weather today"}})(),
        ],
        "search weather today",
        automation,
        system,
    )

    automation.google_search.assert_called_once_with("weather today")
    assert result.success
    assert "Searching Google" in result.message
