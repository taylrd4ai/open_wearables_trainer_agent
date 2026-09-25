"""Open Wearables Personal Trainer - Configuration."""

import json
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    ENV: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    MASTER_KEY: str = "dev-master-key-change-in-production"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/open_wearables"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Biometric provider keys - all optional for mock mode
    WHOOP_CLIENT_ID: str = ""
    WHOOP_CLIENT_SECRET: str = ""
    GARMIN_CLIENT_ID: str = ""
    GARMIN_CLIENT_SECRET: str = ""
    OURA_CLIENT_ID: str = ""
    OURA_CLIENT_SECRET: str = ""
    POLAR_CLIENT_ID: str = ""
    POLAR_CLIENT_SECRET: str = ""

    # Telegram bot - values loaded from .env, never committed
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = ""
    PUBLIC_BASE_URL: str = ""
    ERIC_TELEGRAM_CHAT_ID: int = 0
    # Maps the single current user to their real users.id UUID (as a string),
    # since there's no telegram_chat_id column on User yet. Revisit with a
    # real join table if this ever supports more than one client.
    ERIC_USER_ID: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> List[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                pass
            return [s.strip() for s in v.split(",") if s.strip()]
        if isinstance(v, list):
            return v
        return []


settings = Settings()
