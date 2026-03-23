"""Tests for T19.4: proxy hardening — forwarded_allow_ips config + lifespan warning."""

from unittest.mock import MagicMock, patch

import pytest

from app.main import lifespan


class TestForwardedAllowIpsConfig:
    """T19.4: forwarded_allow_ips setting for proxy hardening."""

    def test_forwarded_allow_ips_default(self):
        """Settings should have forwarded_allow_ips defaulting to '127.0.0.1'."""
        from app.core.config import Settings

        settings = Settings(
            _env_file=None,
            stripe_secret_key="",
            stripe_webhook_secret="",
        )
        assert settings.forwarded_allow_ips == "127.0.0.1"

    def test_forwarded_allow_ips_configurable(self):
        """forwarded_allow_ips should be configurable via env var."""
        from app.core.config import Settings

        settings = Settings(
            _env_file=None,
            stripe_secret_key="",
            stripe_webhook_secret="",
            forwarded_allow_ips="10.0.0.0/8",
        )
        assert settings.forwarded_allow_ips == "10.0.0.0/8"


class TestForwardedAllowIpsWarning:
    """T19.4: Production startup warning when FORWARDED_ALLOW_IPS is default."""

    @pytest.mark.asyncio
    async def test_raises_when_default_in_production(self):
        """Lifespan raises RuntimeError when forwarded_allow_ips is '127.0.0.1' in production."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.clerk_audience = "test-audience"
        mock_settings.turso_database_url = ""
        mock_settings.metrics_api_key = "a-secure-metrics-key-here"
        mock_settings.storage_bucket = "my-bucket"
        mock_settings.forwarded_allow_ips = "127.0.0.1"

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with pytest.raises(RuntimeError, match="FORWARDED_ALLOW_IPS"):
                async with lifespan(test_app):
                    pass

    @pytest.mark.asyncio
    async def test_no_warning_when_configured_in_production(self):
        """Lifespan does not warn when forwarded_allow_ips is customized."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = ""
        mock_settings.metrics_api_key = "a-secure-metrics-key-here"
        mock_settings.storage_bucket = "my-bucket"
        mock_settings.forwarded_allow_ips = "10.0.0.0/8"

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                forwarded_warnings = [
                    call
                    for call in mock_logger.warning.call_args_list
                    if "FORWARDED_ALLOW_IPS" in str(call)
                ]
                assert len(forwarded_warnings) == 0

    @pytest.mark.asyncio
    async def test_no_warning_in_development(self):
        """Lifespan does not warn about forwarded_allow_ips in development."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = ""
        mock_settings.storage_bucket = "my-bucket"
        mock_settings.forwarded_allow_ips = "127.0.0.1"

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                forwarded_warnings = [
                    call
                    for call in mock_logger.warning.call_args_list
                    if "FORWARDED_ALLOW_IPS" in str(call)
                ]
                assert len(forwarded_warnings) == 0
