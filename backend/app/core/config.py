from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Automation Command Center API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    api_v1_prefix: str = "/api/v1"
    secret_key: str = "replace-this-in-production"
    access_token_expire_minutes: int = 120
    algorithm: str = "HS256"

    database_url: str = "sqlite:///./command_center.db"
    redis_url: str = "redis://localhost:6379/0"
    n8n_base_url: str = "http://localhost:5678"
    n8n_api_key: str = ""

    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"

    webhook_signing_secret: str = "replace-webhook-secret"
    rate_limit_per_minute: int = 120

    default_admin_email: str = "admin@command-center.io"
    default_admin_password: str = "ChangeMe!123"
    default_operator_email: str = "operator@command-center.io"
    default_operator_password: str = "ChangeMe!123"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("debug", mode="before")
    @classmethod
    def _normalize_debug(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "prod", "production"}:
                return False
        return False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
