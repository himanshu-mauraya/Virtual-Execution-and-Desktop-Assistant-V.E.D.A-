from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QListWidget,
                               QListWidgetItem, QVBoxLayout, QWidget)


class DashboardPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        title = QLabel("VEDA AI Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: 700; margin-bottom: 12px;")

        subtitle = QLabel("Real-time system intelligence, automation status, and voice assistant metrics.")
        subtitle.setStyleSheet("font-size: 14px; color: #8DA0BE; margin-bottom: 24px;")

        top_panel = QHBoxLayout()
        top_panel.setSpacing(16)
        top_panel.addWidget(self._create_status_card("CPU Usage", "18%", "#5B8DEF"))
        top_panel.addWidget(self._create_status_card("RAM Usage", "43%", "#7C4DFF"))
        top_panel.addWidget(self._create_status_card("Disk", "72%", "#3DDC97"))
        top_panel.addWidget(self._create_status_card("Battery", "84%", "#F7B500"))

        trends = self._create_card("Recent activity", "No activity yet.")
        timeline = self._create_card("Today's tasks", "Review automation workflows, connect AI services, and launch voice assistant.")

        bottom_panel = QHBoxLayout()
        bottom_panel.setSpacing(16)
        bottom_panel.addWidget(trends, 2)
        bottom_panel.addWidget(timeline, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(top_panel)
        layout.addLayout(bottom_panel)
        layout.addStretch(1)

    def _create_status_card(self, label_text: str, value_text: str, accent: str) -> QFrame:
        card = QFrame(self)
        card.setObjectName("card")
        card.setMinimumHeight(120)
        card.setStyleSheet(f"QFrame#card {{ border-left: 5px solid {accent}; }}")

        title = QLabel(label_text)
        title.setStyleSheet("font-size: 13px; color: #8DA0BE; margin-bottom: 8px;")

        value = QLabel(value_text)
        value.setStyleSheet("font-size: 24px; font-weight: 700;")

        inner = QVBoxLayout(card)
        inner.setContentsMargins(20, 16, 20, 16)
        inner.addWidget(title)
        inner.addWidget(value)
        inner.addStretch(1)

        return card

    def _create_card(self, title_text: str, body_text: str) -> QFrame:
        card = QFrame(self)
        card.setObjectName("card")
        card.setMinimumHeight(240)

        title = QLabel(title_text)
        title.setStyleSheet("font-size: 16px; font-weight: 700; margin-bottom: 12px;")

        body = QListWidget(self)
        body.setStyleSheet("QListWidget { background: transparent; border: none; } QLabel { color: #C9D4F0; }")
        body.addItem(QListWidgetItem(body_text))

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(title)
        layout.addWidget(body)
        layout.addStretch(1)
        return card
