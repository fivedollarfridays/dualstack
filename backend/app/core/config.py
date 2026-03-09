"""Configuration management"""

from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    environment: Literal["development", "production"] = "development"

    # Database — DATABASE_URL takes priority for production (e.g. PostgreSQL)
    database_url: str = ""
    turso_database_url: str = ""
    turso_auth_token: str = ""

    # Auth
    clerk_jwks_url: str = ""

    # Payments
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Metrics
    metrics_api_key: str = ""

    # CORS - comma-separated list of allowed origins
    cors_origins: str = "http://localhost:3000"

    @field_validator("stripe_secret_key")
    @classmethod
    def validate_stripe_secret_key(cls, v: str) -> str:
        if v and not v.startswith(("sk_test_", "sk_live_")):
            raise ValueError("stripe_secret_key must start with sk_test_ or sk_live_")
        return v

    @field_validator("stripe_webhook_secret")
    @classmethod
    def validate_stripe_webhook_secret(cls, v: str) -> str:
        if v and not v.startswith("whsec_"):
            raise ValueError("stripe_webhook_secret must start with whsec_")
        return v

    @field_validator("metrics_api_key")
    @classmethod
    def validate_metrics_api_key(cls, v: str) -> str:
        if v and len(v) < 16:
            raise ValueError("metrics_api_key must be at least 16 characters when set")
        return v

    class Config:
        env_file = ".env"

    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
