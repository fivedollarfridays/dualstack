"""Tests for app.core.middleware module."""

import re

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from app.core.middleware import LoggingMiddleware

_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


@pytest.fixture
def middleware_app():
    """Create a FastAPI app with LoggingMiddleware."""
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/ok")
    async def ok_route():
        return {"status": "ok"}

    @app.get("/error")
    async def error_route():
        raise RuntimeError("boom")

    return app


class TestLoggingMiddleware:
    """Test LoggingMiddleware."""

    @pytest.mark.asyncio
    async def test_adds_correlation_id(self, middleware_app):
        """Should add X-Correlation-ID to response headers."""
        transport = ASGITransport(app=middleware_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/ok")
            assert response.status_code == 200
            assert "x-correlation-id" in response.headers

    @pytest.mark.asyncio
    async def test_uses_provided_correlation_id(self, middleware_app):
        """Should use provided X-Correlation-ID if it is a valid UUID."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        transport = ASGITransport(app=middleware_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/ok", headers={"X-Correlation-ID": valid_uuid})
            assert response.headers["x-correlation-id"] == valid_uuid

    @pytest.mark.asyncio
    async def test_replaces_invalid_correlation_id(self, middleware_app):
        """Should replace an invalid X-Correlation-ID with a generated UUID."""
        transport = ASGITransport(app=middleware_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/ok", headers={"X-Correlation-ID": "not-a-uuid"}
            )
            result_id = response.headers["x-correlation-id"]
            assert result_id != "not-a-uuid"
            assert _UUID_PATTERN.match(result_id)

    @pytest.mark.asyncio
    async def test_handles_exceptions(self, middleware_app):
        """Should log and re-raise exceptions from route handlers."""
        # Use raise_server_exceptions=False so httpx catches the 500 response
        # from Starlette's ServerErrorMiddleware instead of re-raising
        transport = ASGITransport(app=middleware_app, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/error")
            # Starlette's ServerErrorMiddleware returns 500
            assert response.status_code == 500
