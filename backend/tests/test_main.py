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


class TestDocsExposure:
    """NEW-002: Swagger UI should be disabled in production."""

    @pytest.mark.asyncio
    async def test_docs_disabled_in_production(self):
        """Production app should return 404 for /docs, /redoc, /openapi.json."""
        from app.main import create_app

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.get_cors_origins.return_value = ["http://localhost:3000"]
        with patch("app.main.get_settings", return_value=mock_settings):
            prod_app = create_app()
        transport = ASGITransport(app=prod_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            for path in ["/docs", "/redoc", "/openapi.json"]:
                response = await client.get(path)
                assert response.status_code == 404, f"{path} should be 404 in production"

    @pytest.mark.asyncio
    async def test_docs_accessible_in_development(self):
        """Development app should return 200 for /docs and /redoc."""
        from app.main import create_app

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.get_cors_origins.return_value = ["http://localhost:3000"]
        with patch("app.main.get_settings", return_value=mock_settings):
            dev_app = create_app()
        transport = ASGITransport(app=dev_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            docs_response = await client.get("/docs")
            assert docs_response.status_code == 200
            redoc_response = await client.get("/redoc")
            assert redoc_response.status_code == 200


class TestCorsHeaders:
    """NEW-008: CORS allow_headers should include X-User-ID in dev mode only."""

    @pytest.mark.asyncio
    async def test_x_user_id_in_dev_cors(self):
        """Development mode should include X-User-ID in CORS allow_headers."""
        from app.main import create_app

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.get_cors_origins.return_value = ["http://localhost:3000"]
        with patch("app.main.get_settings", return_value=mock_settings):
            dev_app = create_app()
        transport = ASGITransport(app=dev_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.options(
                "/",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "X-User-ID",
                },
            )
            allow_headers = response.headers.get("access-control-allow-headers", "")
            assert "x-user-id" in allow_headers.lower()

    @pytest.mark.asyncio
    async def test_x_user_id_not_in_prod_cors(self):
        """Production mode should NOT include X-User-ID in CORS allow_headers."""
        from app.main import create_app

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.get_cors_origins.return_value = ["https://myapp.com"]
        with patch("app.main.get_settings", return_value=mock_settings):
            prod_app = create_app()
        transport = ASGITransport(app=prod_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.options(
                "/",
                headers={
                    "Origin": "https://myapp.com",
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "X-User-ID",
                },
            )
            allow_headers = response.headers.get("access-control-allow-headers", "")
            assert "x-user-id" not in allow_headers.lower()

    @pytest.mark.asyncio
    async def test_dev_mode_cors_no_credentials(self):
        """AUDIT-013: Dev mode should not set allow_credentials=True."""
        from app.main import create_app

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.clerk_jwks_url = ""
        mock_settings.get_cors_origins.return_value = ["http://localhost:3000"]
        with patch("app.main.get_settings", return_value=mock_settings):
            dev_app = create_app()
        transport = ASGITransport(app=dev_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.options(
                "/",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                },
            )
            creds = response.headers.get("access-control-allow-credentials", "")
            assert creds != "true"

    @pytest.mark.asyncio
    async def test_prod_mode_cors_with_credentials(self):
        """AUDIT-013: Production mode (with JWKS) should allow credentials."""
        from app.main import create_app

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.get_cors_origins.return_value = ["https://myapp.com"]
        with patch("app.main.get_settings", return_value=mock_settings):
            prod_app = create_app()
        transport = ASGITransport(app=prod_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.options(
                "/",
                headers={
                    "Origin": "https://myapp.com",
                    "Access-Control-Request-Method": "GET",
                },
            )
            creds = response.headers.get("access-control-allow-credentials", "")
            assert creds == "true"


class TestBodySizeLimit:
    """NEW-009: Oversized request bodies should be rejected."""

    @pytest.mark.asyncio
    async def test_rejects_oversized_body(self):
        """Request with body exceeding limit should return 413."""
        from app.main import create_app

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.get_cors_origins.return_value = ["http://localhost:3000"]
        with patch("app.main.get_settings", return_value=mock_settings):
            test_app = create_app()
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Send a 2MB body (default limit should be 1MB)
            oversized_body = "x" * (2 * 1024 * 1024)
            response = await client.post(
                "/",
                content=oversized_body,
                headers={"Content-Type": "application/json"},
            )
            assert response.status_code == 413


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
        mock_settings.turso_database_url = ""
        mock_settings.metrics_api_key = "a-secure-metrics-key-here"

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
        mock_settings.turso_database_url = ""
        mock_settings.metrics_api_key = "a-secure-metrics-key-here"

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

    @pytest.mark.asyncio
    async def test_raises_with_libsql_url_in_production(self):
        """Lifespan raises RuntimeError when libsql:// URL used in production."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "production"
        mock_settings.stripe_webhook_secret = "whsec_test"
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
        mock_settings.turso_database_url = "libsql://my-db.turso.io"
        mock_settings.metrics_api_key = "a-secure-metrics-key-here"

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with pytest.raises(RuntimeError, match="libsql://"):
                async with lifespan(test_app):
                    pass

    @pytest.mark.asyncio
    async def test_logs_warning_with_libsql_url_in_development(self):
        """Lifespan logs WARNING when libsql:// URL used in development."""
        from fastapi import FastAPI

        mock_settings = MagicMock()
        mock_settings.environment = "development"
        mock_settings.stripe_webhook_secret = ""
        mock_settings.stripe_secret_key = "sk_test_fake"
        mock_settings.clerk_jwks_url = ""
        mock_settings.turso_database_url = "libsql://my-db.turso.io"

        test_app = FastAPI()
        with patch("app.main.get_settings", return_value=mock_settings):
            with patch("app.main.logger") as mock_logger:
                async with lifespan(test_app):
                    pass
                # Should have at least 2 warnings: clerk warning + turso warning
                assert mock_logger.warning.call_count >= 2
                turso_warnings = [
                    call for call in mock_logger.warning.call_args_list
                    if "libsql://" in str(call)
                ]
                assert len(turso_warnings) >= 1

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
                pass  # Should not raise

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
                pass  # Should not raise

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
                # No warnings at all (clerk_jwks_url is set, no turso, stripe_secret_key set)
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
                    call for call in mock_logger.warning.call_args_list
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
                    call for call in mock_logger.warning.call_args_list
                    if "STRIPE_SECRET_KEY" in str(call)
                ]
                assert len(stripe_warnings) == 0
