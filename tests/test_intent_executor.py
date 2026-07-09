from unittest.mock import Mock

from src.veda_ai.core.command_engine import CommandEngine, Intent
from src.veda_ai.core.intent_executor import IntentExecutor


def test_execute_open_app_intent_calls_automation() -> None:
    automation = Mock()
    system = Mock()
    executor = IntentExecutor()
    intent = Intent(intent="open_app", target="vscode", confidence=0.95)

    result = executor.execute_intent(intent, "open VS Code", automation, system)

    automation.open_application.assert_called_once_with("open VS Code")
    assert result.success is True
    assert "Opening vscode" in result.message


def test_execute_screenshot_intent_calls_automation() -> None:
    automation = Mock()
    system = Mock()
    executor = IntentExecutor()
    intent = Intent(intent="screenshot")

    result = executor.execute_intent(intent, "take a screenshot", automation, system)

    automation.take_screenshot.assert_called_once_with("veda_screenshot.png")
    assert result.success is True
    assert "Screenshot captured" in result.message


def test_execute_shutdown_intent_calls_system() -> None:
    automation = Mock()
    system = Mock()
    executor = IntentExecutor()
    intent = Intent(intent="shutdown")

    result = executor.execute_intent(intent, "shutdown the computer", automation, system)

    system.shutdown.assert_called_once()
    assert result.success is True
    assert "shutdown initiated" in result.message


def test_execute_search_intent_opens_browser() -> None:
    automation = Mock()
    system = Mock()
    executor = IntentExecutor()
    intent = Intent(intent="search")

    result = executor.execute_intent(intent, "search for open source voice assistant", automation, system)

    automation.search_web.assert_called_once_with("search for open source voice assistant")
    assert result.success is True
    assert "Searching the web" in result.message


def test_execute_unknown_intent_returns_false() -> None:
    automation = Mock()
    system = Mock()
    executor = IntentExecutor()
    intent = Intent(intent="unknown")

    result = executor.execute_intent(intent, "do nothing", automation, system)

    assert automation.open_application.call_count == 0
    assert automation.take_screenshot.call_count == 0
    assert system.shutdown.call_count == 0
    assert result.success is False
    assert "couldn't understand" in result.message
