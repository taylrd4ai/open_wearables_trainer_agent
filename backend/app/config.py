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
    # Verify host/service name and db name against docker-compose; keep the
    # trainer DB separate from the Open Wearables platform's own database.
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/ow_trainer"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3001",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # # Primary: OpenRouter (free-tier model), Fallback: local Ollama
    # OPENROUTER_API_KEY: str = ""
    # OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"     
    # OPENROUTER_MODEL: str = "openrouter/free"
    # OPENROUTER_SITE_URL: str = "http://localhost:3001"   # required by OpenRouter for free tier attribution
    # OPENROUTER_APP_NAME: str = "open-wearables-trainer"
    #
    # OLLAMA_BASE_URL: str = "http://host.docker.internal:11434/v1"
    # OLLAMA_MODEL: str = "qwen3:8b"
    #
    # LLM_TIMEOUT_SECONDS: float = 15.0

    # Open Wearables platform connection (OW owns provider OAuth + tokens).
    # Set real values in a gitignored .env or compose environment — never commit.
    OPEN_WEARABLES_BASE_URL: str = "http://host.docker.internal:8000"
    OPEN_WEARABLES_API_KEY: str = ""
    OPEN_WEARABLES_USER_ID: str = ""

    # Legacy direct-provider OAuth creds (unused with OW-integrated providers).
    # Kept so the oura.py / polar.py stubs keep importing cleanly.
    WHOOP_CLIENT_ID: str = ""
    WHOOP_CLIENT_SECRET: str = ""
    GARMIN_CLIENT_ID: str = ""
    GARMIN_CLIENT_SECRET: str = ""
    OURA_CLIENT_ID: str = ""
    OURA_CLIENT_SECRET: str = ""
    POLAR_CLIENT_ID: str = ""
    POLAR_CLIENT_SECRET: str = ""

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
