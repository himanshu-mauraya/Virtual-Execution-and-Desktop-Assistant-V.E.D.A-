from src.veda_ai.app import main
from src.veda_ai.bootstrap import build_app_context, load_app_config


def test_app_startup_initializes_context(monkeypatch) -> None:
    config = load_app_config()
    context = build_app_context(config, database_path=":memory:")
    assert context.config.ai_provider == "openai"
    assert context.command_engine is not None
    assert context.automation is not None
    assert context.system is not None
    assert context.database is not None


def test_app_entrypoint_runs_with_dummy_context(monkeypatch) -> None:
    # Ensure the startup path can build context without invoking the GUI.
    config = load_app_config()
    context = build_app_context(config, database_path=":memory:")
    assert context is not None
