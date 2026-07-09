from unittest.mock import Mock, patch

from src.veda_ai.automation.controller import AutomationController


def test_open_browser_opens_default_search_when_binary_missing(monkeypatch):
    automation = AutomationController()
    with patch("src.veda_ai.automation.controller.subprocess.Popen", side_effect=Exception("missing")):
        with patch("src.veda_ai.automation.controller.webbrowser.open") as mock_open:
            automation.open_application("open chrome")
            mock_open.assert_called_once_with("https://www.google.com")


def test_open_browser_tries_brave_before_default(monkeypatch):
    automation = AutomationController()
    mock_popen = Mock()
    with patch("src.veda_ai.automation.controller.subprocess.Popen", mock_popen):
        automation.open_application("open brave")
        mock_popen.assert_called_once_with(["brave"])


def test_open_edge_uses_msedge(monkeypatch):
    automation = AutomationController()
    mock_popen = Mock()
    with patch("src.veda_ai.automation.controller.subprocess.Popen", mock_popen):
        automation.open_application("open edge")
        mock_popen.assert_called_once_with(["msedge"])


def test_open_spotify_uses_spotify_executable_or_web(monkeypatch):
    automation = AutomationController()
    mock_popen = Mock(side_effect=[Exception("fail"), Exception("fail")])
    with patch("src.veda_ai.automation.controller.subprocess.Popen", mock_popen):
        with patch("src.veda_ai.automation.controller.webbrowser.open") as mock_open:
            automation.open_application("open spotify")
            mock_open.assert_called_once_with("https://open.spotify.com")


def test_open_explorer_falls_back_to_explorer(monkeypatch):
    automation = AutomationController()
    with patch("src.veda_ai.automation.controller.os.startfile", side_effect=Exception("fail")):
        with patch("src.veda_ai.automation.controller.subprocess.Popen") as mock_popen:
            automation.open_application("open explorer")
            mock_popen.assert_called_once_with(["explorer"])
