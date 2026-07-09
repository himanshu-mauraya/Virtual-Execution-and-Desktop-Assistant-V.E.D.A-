from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget


class SideNavigation(QWidget):
    page_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setObjectName("sideNavigation")
        self._create_layout()

    def _create_layout(self) -> None:
        self._navigation = QListWidget(self)
        self._navigation.setSpacing(6)
        self._navigation.setSelectionMode(QListWidget.SingleSelection)
        self._navigation.setFocusPolicy(Qt.NoFocus)
        self._navigation.setStyleSheet("QListWidget { padding: 16px; }")

        options = [
            ("dashboard", "🏠 Dashboard"),
            ("voice", "🎤 Voice Assistant"),
            ("ai_chat", "🤖 AI Chat"),
            ("automation", "⚡ Automation"),
            ("file_manager", "📁 File Manager"),
            ("browser", "🌐 Browser Automation"),
            ("email", "📧 Email Automation"),
            ("scheduler", "📅 Scheduler"),
            ("analytics", "📊 Analytics"),
            ("memory", "🧠 AI Memory"),
            ("settings", "⚙ Settings"),
        ]

        for key, title in options:
            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, key)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self._navigation.addItem(item)

        self._navigation.currentItemChanged.connect(self._on_selection_changed)
        self._navigation.setCurrentRow(0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._navigation)

    def _on_selection_changed(self, current: QListWidgetItem | None) -> None:
        if current is None:
            return
        page_key = current.data(Qt.UserRole)
        if page_key:
            self.page_requested.emit(page_key)
