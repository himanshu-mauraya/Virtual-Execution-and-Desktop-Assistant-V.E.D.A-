from __future__ import annotations

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
    )

    ai_provider: str = Field("openai", description="Default AI provider.")
    openai_api_key: str | None = Field(None, description="OpenAI API key.")
    voice_enabled: bool = Field(True, description="Enable voice assistant features.")
    offline_mode: bool = Field(False, description="Enable offline-first mode.")
    log_level: str = Field("INFO", description="Default logging level.")


__all__ = ["AppConfig"]
