from __future__ import annotations

PRIMARY = "#5B8DEF"
ACCENT = "#7C4DFF"
BACKGROUND = "#0B0F19"
CARD = "#161B26"
FOREGROUND = "#E6ECF5"
SECONDARY = "#8DA0BE"
SUCCESS = "#3DDC97"
DANGER = "#FF5A5A"
WARNING = "#F7B500"

GLOBAL_STYLES = f"""
QWidget {{
    background-color: {BACKGROUND};
    color: {FOREGROUND};
    font-family: Segoe UI, Arial, sans-serif;
}}
QMainWindow {{
    background-color: transparent;
}}
QToolTip {{
    background-color: {CARD};
    color: {FOREGROUND};
    border: 1px solid rgba(255,255,255,0.08);
}}
QLineEdit, QTextEdit {{
    background-color: #121827;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 10px;
    color: {FOREGROUND};
}}
QPushButton {{
    border-radius: 12px;
    padding: 10px 16px;
    background-color: {PRIMARY};
    border: none;
    color: white;
}}
QPushButton:hover {{
    background-color: #4E78D9;
}}
QPushButton:disabled {{
    background-color: rgba(91, 141, 239, 0.45);
}}
QListWidget {{
    background-color: transparent;
    border: none;
}}
QListWidget::item {{
    padding: 14px 16px;
    border-radius: 14px;
}}
QListWidget::item:selected {{
    background-color: rgba(91, 141, 239, 0.18);
    color: {FOREGROUND};
}}
QFrame#card {{
    background-color: {CARD};
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
}}
"""
