"""Tests for app.main lifespan startup checks."""

from unittest.mock import MagicMock, patch

import pytest

from app.main import lifespan


class TestLifespanBasic:
    """Basic lifespan startup/shutdown tests."""

    @pytest.mark.asyncio
    async def test_lifespan_yields_in_dev(self):
        """Lifespan yields without error in development mode."""
        from fastapi import FastAPI

        test_app = FastAPI()
        async with lifespan(test_app):
            pass

    @pytest.mark.asyncio
    async def test_sets_stripe_api_key_at_startup(self):
        """Lifespan sets stripe.api_key from settings."""
        import stripe
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_startup_key"
        mock_settings.turso_database_url = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            async with lifespan(test_app):
                assert stripe.api_key == "sk_test_startup_key"


class TestLifespanProductionChecks:
    """Production startup RuntimeError checks."""

    @pytest.mark.asyncio
    async def test_raises_without_webhook_secret_in_production(self):
        """Lifespan raises RuntimeError in production without webhook secret."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with pytest.raises(RuntimeError, match="STRIPE_WEBHOOK_SECRET"):
                async with lifespan(test_app):
                    pass

    @pytest.mark.asyncio
    async def test_allows_production_with_webhook_secret(self):
        """Lifespan succeeds in production when webhook secret is set."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.turso_database_url = ""
        mock_settings.metrics_api_key = "a-secure-metrics-key-here"

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            async with lifespan(test_app):
                pass

    @pytest.mark.asyncio
    async def test_raises_without_clerk_jwks_url_in_production(self):
        """Lifespan raises RuntimeError in production without clerk_jwks_url."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with pytest.raises(RuntimeError, match="CLERK_JWKS_URL"):
                async with lifespan(test_app):
                    pass

    @pytest.mark.asyncio
    async def test_allows_production_with_clerk_jwks_url(self):
        """Lifespan succeeds in production when clerk_jwks_url is set."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = ""
        mock_settings.metrics_api_key = "a-secure-metrics-key-here"

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            async with lifespan(test_app):
                pass

    @pytest.mark.asyncio
    async def test_raises_without_metrics_api_key_in_production(self):
        """SEC-003: Lifespan raises RuntimeError in production without METRICS_API_KEY."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = ""
        mock_settings.metrics_api_key = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with pytest.raises(RuntimeError, match="METRICS_API_KEY"):
                async with lifespan(test_app):
                    pass

    @pytest.mark.asyncio
    async def test_allows_dev_without_metrics_api_key(self):
        """SEC-003: Development startup works without METRICS_API_KEY."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = ""
        mock_settings.metrics_api_key = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            async with lifespan(test_app):
                pass

    @pytest.mark.asyncio
    async def test_allows_production_with_metrics_api_key(self):
        """SEC-003: Production startup succeeds when METRICS_API_KEY is set."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = ""
        mock_settings.metrics_api_key = "a-secure-metrics-key-here"

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            async with lifespan(test_app):
                pass


class TestClerkAudienceStartup:
    """T25.1: CLERK_AUDIENCE enforcement at startup."""

    @pytest.mark.asyncio
    async def test_raises_without_clerk_audience_in_production(self):
        """Production startup fails when CLERK_JWKS_URL is set but CLERK_AUDIENCE is empty."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.clerk_audience = ""
        mock_settings.metrics_api_key = "a-secure-metrics-key-here"
        mock_settings.turso_database_url = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with pytest.raises(RuntimeError, match="CLERK_AUDIENCE"):
                async with lifespan(test_app):
                    pass

    @pytest.mark.asyncio
    async def test_allows_production_with_clerk_audience(self):
        """Production startup succeeds when both CLERK_JWKS_URL and CLERK_AUDIENCE are set."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.clerk_audience = "my-app"
        mock_settings.metrics_api_key = "a-secure-metrics-key-here"
        mock_settings.turso_database_url = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            async with lifespan(test_app):
                pass

    @pytest.mark.asyncio
    async def test_no_raise_without_jwks_and_audience_in_production(self):
        """Production checks CLERK_JWKS_URL before CLERK_AUDIENCE."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = ""
        mock_settings.clerk_audience = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with pytest.raises(RuntimeError, match="CLERK_JWKS_URL"):
                async with lifespan(test_app):
                    pass

    @pytest.mark.asyncio
    async def test_warns_without_clerk_audience_in_dev(self):
        """Non-production emits warning when CLERK_AUDIENCE is empty but JWKS is set."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.clerk_audience = ""
        mock_settings.turso_database_url = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                audience_warnings = [
                    call
                    for call in mock_logger.warning.call_args_list
                    if "CLERK_AUDIENCE" in str(call)
                ]
                assert len(audience_warnings) >= 1

    @pytest.mark.asyncio
    async def test_no_audience_warning_when_set_in_dev(self):
        """No audience warning when CLERK_AUDIENCE is configured in dev."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.clerk_audience = "my-app"
        mock_settings.turso_database_url = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                audience_warnings = [
                    call
                    for call in mock_logger.warning.call_args_list
                    if "CLERK_AUDIENCE" in str(call)
                ]
                assert len(audience_warnings) == 0


class TestLifespanWarnings:
    """Lifespan warning tests for dev mode."""

    @pytest.mark.asyncio
    async def test_logs_warning_when_clerk_jwks_url_empty(self):
        """Lifespan logs a loud warning in dev mode without clerk_jwks_url."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = ""
        mock_settings.turso_database_url = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                mock_logger.warning.assert_called_once()
                warning_msg = mock_logger.warning.call_args[0][0]
                assert "CLERK_JWKS_URL" in warning_msg

    @pytest.mark.asyncio
    async def test_no_warning_when_clerk_jwks_url_set(self):
        """Lifespan does not log warning when clerk_jwks_url is set."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                mock_logger.warning.assert_not_called()

    @pytest.mark.asyncio
    async def test_logs_warning_without_clerk_in_development(self):
        """Lifespan logs WARNING when Clerk is not configured in development."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = ""
        mock_settings.turso_database_url = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                assert mock_logger.warning.call_count >= 1
                clerk_warnings = [
                    call
                    for call in mock_logger.warning.call_args_list
                    if "Clerk" in str(call)
                ]
                assert len(clerk_warnings) >= 1

    @pytest.mark.asyncio
    async def test_no_turso_warning_without_libsql_url(self):
        """Lifespan does not warn about Turso when URL is not libsql://."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                mock_logger.warning.assert_not_called()

    @pytest.mark.asyncio
    async def test_logs_warning_when_stripe_secret_key_empty(self):
        """AUDIT-016: Lifespan logs warning in dev when stripe_secret_key is empty."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = ""
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                stripe_warnings = [
                    call
                    for call in mock_logger.warning.call_args_list
                    if "STRIPE_SECRET_KEY" in str(call)
                ]
                assert len(stripe_warnings) == 1

    @pytest.mark.asyncio
    async def test_no_stripe_warning_when_key_set(self):
        """AUDIT-016: No stripe warning when stripe_secret_key is configured."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                stripe_warnings = [
                    call
                    for call in mock_logger.warning.call_args_list
                    if "STRIPE_SECRET_KEY" in str(call)
                ]
                assert len(stripe_warnings) == 0


class TestStorageConfig:
    """Test storage configuration fields in Settings."""

    def test_storage_fields_exist_with_defaults(self):
        """Settings should have 5 storage fields with empty/default values."""
        from app.core.config import Settings

        settings = Settings(
            _env_file=None,
            stripe_secret_key="",
            stripe_webhook_secret="",
        )
        assert settings.storage_bucket == ""
        assert settings.storage_access_key == ""
        assert settings.storage_secret_key == ""
        assert settings.storage_endpoint == ""
        assert settings.storage_region == "us-east-1"


class TestStorageWarning:
    """Test production startup warning when storage is not configured."""

    @pytest.mark.asyncio
    async def test_logs_warning_when_storage_not_configured(self):
        """Lifespan logs warning in dev when storage_bucket is empty."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = ""
        mock_settings.storage_bucket = ""

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                storage_warnings = [
                    call
                    for call in mock_logger.warning.call_args_list
                    if "storage" in str(call).lower()
                ]
                assert len(storage_warnings) >= 1

    @pytest.mark.asyncio
    async def test_no_storage_warning_when_configured(self):
        """Lifespan does not warn about storage when bucket is configured."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = ""
        mock_settings.storage_bucket = "my-bucket"

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                storage_warnings = [
                    call
                    for call in mock_logger.warning.call_args_list
                    if "storage" in str(call).lower()
                ]
                assert len(storage_warnings) == 0
