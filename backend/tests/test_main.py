"""Tests for app.main module."""

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


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
                assert response.status_code == 404, (
                    f"{path} should be 404 in production"
                )

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


class TestRouterRegistration:
    """Test that all routers are registered on the application."""

    @pytest.mark.asyncio
    async def test_files_router_mounted(self):
        """Files router should be mounted at /api/v1/files."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # GET /api/v1/files should not return 404 (may return 401/403)
            response = await client.get("/api/v1/files")
            assert response.status_code != 404, (
                "Files router not mounted — GET /api/v1/files returned 404"
            )

    @pytest.mark.asyncio
    async def test_ws_router_mounted(self):
        """WebSocket router should be mounted at /ws."""
        # Verify the route exists in the app's routes
        ws_paths = [
            route.path
            for route in app.routes
            if hasattr(route, "path") and route.path == "/ws"
        ]
        assert len(ws_paths) == 1, "WebSocket route /ws not found in app routes"


