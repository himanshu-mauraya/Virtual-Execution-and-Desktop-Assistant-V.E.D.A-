from PySide6.QtWidgets import QApplication

from src.veda_ai.ui.pages.voice_assistant import VoiceAssistantPage


def test_voice_assistant_page_sets_microphone_status() -> None:
    app = QApplication.instance() or QApplication([])
    page = VoiceAssistantPage()

    page.set_microphone_status(True)

    assert "available" in page.microphone_label.text().lower()
    assert page.listen_button.isEnabled()


def test_voice_assistant_page_emits_text_command_signal() -> None:
    app = QApplication.instance() or QApplication([])
    page = VoiceAssistantPage()
    received: list[str] = []

    def on_text(text: str) -> None:
        received.append(text)

    page.text_command_submitted.connect(on_text)
    page.command_input.setText("open vscode")
    page._submit_text_command()

    assert received == ["open vscode"]
    assert "Text: open vscode" in page.transcription_output.toPlainText()


def test_voice_assistant_page_displays_response() -> None:
    app = QApplication.instance() or QApplication([])
    page = VoiceAssistantPage()
    page.display_response("All done")

    assert "VEDA: All done" in page.transcription_output.toPlainText()


def test_voice_assistant_page_sets_recognizer_status() -> None:
    app = QApplication.instance() or QApplication([])
    page = VoiceAssistantPage()

    page.set_recognizer_status("VoskRecognizer")

    assert "voskrecognizer" in page.recognizer_label.text().lower()
