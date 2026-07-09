from __future__ import annotations

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class VoiceAssistantPage(QWidget):
    start_listening = Signal()
    stop_listening = Signal()
    text_command_submitted = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._update_state(ready=True)

    def _build_ui(self) -> None:
        title = QLabel("Voice Assistant")
        title.setStyleSheet("font-size: 28px; font-weight: 700; margin-bottom: 12px;")

        subtitle = QLabel("Start speaking to control VEDA.")
        subtitle.setStyleSheet("font-size: 14px; color: #8DA0BE; margin-bottom: 24px;")

        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("font-size: 14px; color: #8DA0BE; margin-bottom: 8px;")

        self.microphone_label = QLabel("Microphone: unavailable")
        self.microphone_label.setStyleSheet("font-size: 12px; color: #7C4DFF; margin-bottom: 16px;")

        self.recognizer_label = QLabel("Recognizer: none")
        self.recognizer_label.setStyleSheet("font-size: 12px; color: #8DA0BE; margin-bottom: 16px;")

        self.transcription_output = QTextEdit(self)
        self.transcription_output.setReadOnly(True)
        self.transcription_output.setMinimumHeight(220)
        self.transcription_output.setStyleSheet("background-color: #121827; color: #E6ECF5; border-radius: 14px;")

        # Response card area (scrollable vertical list)
        self.response_area = QScrollArea(self)
        self.response_area.setWidgetResizable(True)
        self._response_container = QWidget()
        self._response_layout = QVBoxLayout(self._response_container)
        self._response_layout.setContentsMargins(0, 0, 0, 0)
        self._response_layout.setSpacing(8)
        self._response_layout.addStretch(1)
        self.response_area.setWidget(self._response_container)

        self.command_input = QLineEdit(self)
        self.command_input.setPlaceholderText("Type a command instead of speaking...")
        self.command_input.setStyleSheet("background-color: #0F172A; color: #E6ECF5; border-radius: 10px; padding: 8px;")

        self.command_submit = QPushButton("Send Text Command")
        self.command_submit.clicked.connect(self._submit_text_command)

        command_row = QHBoxLayout()
        command_row.addWidget(self.command_input, 1)
        command_row.addWidget(self.command_submit)

        self.listen_button = QPushButton("Start Listening")
        self.listen_button.clicked.connect(self._toggle_listening)

        control_panel = QHBoxLayout()
        control_panel.addWidget(self.listen_button)
        control_panel.addStretch(1)

        self.fallback_label = QLabel("Text commands are always available.")
        self.fallback_label.setStyleSheet("font-size: 12px; color: #8DA0BE; margin-bottom: 8px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.status_label)
        layout.addWidget(self.microphone_label)
        layout.addWidget(self.recognizer_label)
        layout.addWidget(self.fallback_label)
        layout.addWidget(self.transcription_output)
        layout.addWidget(self.response_area)
        layout.addLayout(command_row)
        layout.addLayout(control_panel)
        layout.addStretch(1)

        self._listening = False

    def _toggle_listening(self) -> None:
        if self._listening:
            self.stop_listening.emit()
        else:
            self.start_listening.emit()

    def _submit_text_command(self) -> None:
        text = self.command_input.text().strip()
        if not text:
            return

        self.command_input.clear()
        self.text_command_submitted.emit(text)
        self.display_transcription(f"Text: {text}")

    def _update_state(self, ready: bool = False, listening: bool = False) -> None:
        self._listening = listening
        if listening:
            self.status_label.setText("Status: Listening...")
            self.listen_button.setText("Stop Listening")
        elif ready:
            self.status_label.setText("Status: Idle")
            self.listen_button.setText("Start Listening")

    def set_listening_state(self) -> None:
        self._update_state(listening=True)

    def set_ready_state(self) -> None:
        self._update_state(ready=True)

    def set_microphone_status(self, available: bool) -> None:
        if available:
            self.microphone_label.setText("Microphone: available")
            self.microphone_label.setStyleSheet("font-size: 12px; color: #3DDC97; margin-bottom: 16px;")
            self.listen_button.setEnabled(True)
        else:
            self.microphone_label.setText("Microphone: unavailable")
            self.microphone_label.setStyleSheet("font-size: 12px; color: #FF5A5A; margin-bottom: 16px;")
            self.listen_button.setEnabled(False)

    def set_recognizer_status(self, name: str) -> None:
        self.recognizer_label.setText(f"Recognizer: {name}")

    def display_transcription(self, text: str) -> None:
        self.transcription_output.append(text)

    def display_response(self, text: str) -> None:
        # Distinguish assistant responses in the transcript view with a timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%I:%M:%S %p")
        self.transcription_output.append(f"[{timestamp}] VEDA: {text}")
        self._add_response_card(timestamp, text)

    def _add_response_card(self, timestamp: str, text: str) -> None:
        card = QFrame(self._response_container)
        card.setObjectName("responseCard")
        card.setStyleSheet(
            "QFrame#responseCard { background-color: #0B1220; border-radius: 10px; padding: 10px; }"
        )
        title = QLabel(f"VEDA — {timestamp}", card)
        title.setStyleSheet("font-size: 12px; color: #8DA0BE; margin-bottom: 6px;")
        body = QLabel(text, card)
        body.setWordWrap(True)
        body.setStyleSheet("font-size: 14px; color: #E6ECF5;")

        v = QVBoxLayout(card)
        v.setContentsMargins(8, 8, 8, 8)
        v.addWidget(title)
        v.addWidget(body)

        # Insert before the stretch so newest are on top
        self._response_layout.insertWidget(self._response_layout.count() - 1, card)
