from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget


class PagePlaceholder(QWidget):
    def __init__(self, title: str, subtitle: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui(title, subtitle)

    def _build_ui(self, title_text: str, subtitle_text: str) -> None:
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 28px; font-weight: 700; margin-bottom: 12px;")

        subtitle = QLabel(subtitle_text)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("font-size: 14px; color: #8DA0BE; margin-bottom: 24px;")

        info = QLabel("This page is under active development and will receive AI-driven controls, automation tools, and responsive workflows.")
        info.setStyleSheet("font-size: 13px; color: #C9D4F0;")
        info.setAlignment(Qt.AlignTop)
        info.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(info)
        layout.addStretch(1)
