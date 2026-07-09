from src.veda_ai.core.command_engine import CommandEngine


def test_classify_open_command() -> None:
    engine = CommandEngine()
    intention = engine.classify("open VS Code")
    assert intention.intent == "open_app"
    assert intention.target == "vscode"


def test_classify_screenshot_command() -> None:
    engine = CommandEngine()
    intention = engine.classify("take a screenshot")
    assert intention.intent == "screenshot"


def test_classify_restart_command() -> None:
    engine = CommandEngine()
    intention = engine.classify("restart the computer")
    assert intention.intent == "restart"


def test_classify_lock_command() -> None:
    engine = CommandEngine()
    intention = engine.classify("lock my workstation")
    assert intention.intent == "lock"


def test_classify_sleep_command() -> None:
    engine = CommandEngine()
    intention = engine.classify("put the PC to sleep")
    assert intention.intent == "sleep"


def test_classify_search_command() -> None:
    engine = CommandEngine()
    intention = engine.classify("search for weather forecast")
    assert intention.intent == "search"


def test_classify_unknown_command() -> None:
    engine = CommandEngine()
    intention = engine.classify("")
    assert intention.intent == "unknown"
    assert intention.confidence == 1.0
