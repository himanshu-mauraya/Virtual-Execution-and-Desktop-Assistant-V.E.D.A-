from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget


class TopBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("topBar")
        self._build_ui()

    def _build_ui(self) -> None:
        self.search_field = QLineEdit(self)
        self.search_field.setPlaceholderText("Search commands, apps, settings...")

        self.microphone_status = QLabel("⚪ Idle")
        self.recognizer_status = QLabel("Recognizer: none")
        self.network_status = QLabel("🌐 Online")
        self.battery_status = QLabel("🔋 84%")
        self.clock = QLabel("00:00")
        self.profile = QLabel("👤 Veda")

        for label in (self.microphone_status, self.recognizer_status, self.network_status, self.battery_status, self.clock, self.profile):
            label.setContentsMargins(8, 0, 8, 0)
            label.setStyleSheet("color: #8DA0BE;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(16)
        layout.addWidget(self.search_field, 1)
        layout.addWidget(self.microphone_status)
        layout.addWidget(self.recognizer_status)
        layout.addWidget(self.network_status)
        layout.addWidget(self.battery_status)
        layout.addWidget(self.clock)
        layout.addWidget(self.profile)
        layout.setAlignment(Qt.AlignVCenter)
