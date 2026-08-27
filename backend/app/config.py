"""Centralised runtime configuration.

Everything the app needs to run is read from the environment (or a local
``backend/.env`` file) exactly once, here, and imported as ``settings``
everywhere else. No module reads ``os.environ`` directly.
"""
import json
from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ----- environment -----
    app_env: str = Field(default="development")  # "development" | "production"
    app_version: str = Field(default="0.2.0")
    log_level: str = Field(default="INFO")

    # ----- database -----
    # Default points at the docker-compose service; override for bare-metal.
    database_url: str = Field(
        default="postgresql+psycopg://sahaj:sahaj@localhost:5432/sahaj"
    )

    # ----- CORS -----
    # NoDecode: stop pydantic-settings from JSON-decoding the raw env value so a
    # plain comma-separated string reaches _split_origins below.
    backend_cors_origins: Annotated[list[str], NoDecode] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://[::1]:3000",
        ]
    )

    # ----- auth -----
    session_ttl_seconds: int = Field(default=7 * 24 * 60 * 60)
    reset_token_ttl_seconds: int = Field(default=60 * 60)
    pbkdf2_iterations: int = Field(default=200_000)

    # ----- rate limiting (slowapi syntax) -----
    rate_limit_default: str = Field(default="120/minute")
    rate_limit_auth: str = Field(default="20/minute")
    rate_limit_multimodal: str = Field(default="12/minute")

    # ----- Groq multimodal -----
    groq_api_key: str = Field(default="")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1")
    groq_vision_model: str = Field(default="meta-llama/llama-4-scout-17b-16e-instruct")
    groq_transcribe_model: str = Field(default="whisper-large-v3-turbo")
    groq_text_model: str = Field(default="llama-3.3-70b-versatile")
    groq_timeout_seconds: float = Field(default=45.0)

    # ----- upload guards -----
    max_upload_mb_image: int = Field(default=10)
    max_upload_mb_audio: int = Field(default=25)

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, v):
        """Accept either a JSON list or a plain comma-separated string."""
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            if s.startswith("["):
                return json.loads(s)
            return [part.strip() for part in s.split(",") if part.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def groq_enabled(self) -> bool:
        return bool(self.groq_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
