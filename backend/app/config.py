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

    # Open Wearables platform client (app/services/ow_client.py) -- OW owns
    # provider OAuth/token storage; we just pull normalized data through it.
    OPEN_WEARABLES_BASE_URL: str = "http://localhost:8000"
    OPEN_WEARABLES_API_KEY: str = ""
    OPEN_WEARABLES_USER_ID: str = ""

    # Biometric provider keys - all optional for mock mode
    WHOOP_CLIENT_ID: str = ""
    WHOOP_CLIENT_SECRET: str = ""
    GARMIN_CLIENT_ID: str = ""
    GARMIN_CLIENT_SECRET: str = ""
    OURA_CLIENT_ID: str = ""
    OURA_CLIENT_SECRET: str = ""
    POLAR_CLIENT_ID: str = ""
    POLAR_CLIENT_SECRET: str = ""

    # LLM client (app/services/llm_client.py) -- OpenRouter primary with
    # native model-fallback routing, local Ollama as final fallback.
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_SITE_URL: str = "http://localhost:3001"
    OPENROUTER_APP_NAME: str = "Open Wearables Trainer"
    # Comma-separated in .env, e.g.:
    #   OPENROUTER_MODELS=openrouter/free,meta-llama/llama-3.1-8b-instruct,mistralai/mistral-7b-instruct
    # Parsed into a list via the field_validator below. Primary model is the
    # first entry; up to 3 more are passed as OpenRouter's native fallback array.
    OPENROUTER_MODELS: List[str] = ["openrouter/free"]
    LLM_TIMEOUT_SECONDS: float = 30.0
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434/v1"
    OLLAMA_MODEL: str = "qwen3:8b"

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

    @field_validator("CORS_ORIGINS", "OPENROUTER_MODELS", mode="before")
    @classmethod
    def parse_comma_or_json_list(cls, v: object) -> List[str]:
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

    @property
    def openrouter_models(self) -> List[str]:
        """
        Lowercase alias matching llm_client.py's settings.openrouter_models
        usage (llm_client.py was written against a lowercase attribute name;
        OPENROUTER_MODELS above is the actual env-loaded field).
        """
        return self.OPENROUTER_MODELS


settings = Settings()
