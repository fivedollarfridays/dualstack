"""Tests for app.main module."""

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app, lifespan


class TestRootEndpoint:
    """Test GET / endpoint."""

    @pytest.mark.asyncio
    async def test_returns_200(self):
        """GET / should return 200."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_returns_api_message(self):
        """GET / should return DualStack API message."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            data = response.json()
            assert data["message"] == "DualStack API"
            assert data["status"] == "running"


class TestLifespan:
    """Test app lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_yields_in_dev(self):
        """Lifespan yields without error in development mode."""
        from fastapi import FastAPI

        test_app = FastAPI()
        async with lifespan(test_app):
            pass  # Startup and shutdown should work

    @pytest.mark.asyncio
    async def test_raises_without_webhook_secret_in_production(self):
        """Lifespan raises RuntimeError in non-dev without webhook secret."""
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

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            async with lifespan(test_app):
                pass  # Should not raise

    @pytest.mark.asyncio
    async def test_raises_without_clerk_jwks_url_in_production(self):
        """Lifespan raises RuntimeError in non-dev without clerk_jwks_url."""
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

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            async with lifespan(test_app):
                pass  # Should not raise

    @pytest.mark.asyncio
    async def test_logs_warning_when_clerk_jwks_url_empty(self):
        """Lifespan logs a loud warning in dev mode without clerk_jwks_url."""
        import logging
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = ""

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

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                mock_logger.warning.assert_not_called()

    @pytest.mark.asyncio
    async def test_sets_stripe_api_key_at_startup(self):
        """Lifespan sets stripe.api_key from settings."""
        import stripe
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_startup_key"

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            async with lifespan(test_app):
                assert stripe.api_key == "sk_test_startup_key"
