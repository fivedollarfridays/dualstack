"""Configuration management"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    environment: str = "development"

    # Database
    turso_database_url: str = ""
    turso_auth_token: str = ""

    # Auth
    clerk_secret_key: str = ""
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

    # Add your app-specific settings below

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
