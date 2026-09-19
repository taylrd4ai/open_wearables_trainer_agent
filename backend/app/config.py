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
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/ow_trainer"
    CORS_ORIGINS: List[str] = ["http://localhost:3001", "http://localhost:8000"]

    # Open Wearables platform connection (OW owns provider OAuth + tokens)
    OPEN_WEARABLES_BASE_URL: str = "http://host.docker.internal:8000"
    OPEN_WEARABLES_API_KEY: str = "sk-5f2d7d1dd1712ddf79e558e7d5531384"
    OPEN_WEARABLES_USER_ID: str = "b7435467-702d-4aba-b71f-13358eb25736"

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
