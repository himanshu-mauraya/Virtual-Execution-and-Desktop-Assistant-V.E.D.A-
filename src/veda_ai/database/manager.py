from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class DatabaseManager:
    """Lightweight SQLite persistence layer for VEDA AI."""

    def __init__(self, database_path: str | Path = "veda_ai.db") -> None:
        self.database_path = Path(database_path)
        self.connection = sqlite3.connect(str(self.database_path), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def get_setting(self, key: str) -> str | None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else None

    def set_setting(self, key: str, value: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?)"
            " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
