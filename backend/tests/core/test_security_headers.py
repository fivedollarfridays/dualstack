"""Tests for security headers middleware."""

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from app.core.security_headers import SecurityHeadersMiddleware


@pytest.fixture
def app_with_headers():
    """Create a test app with security headers middleware."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/test")
    async def test_route():
        return {"ok": True}

    return app


class TestSecurityHeadersMiddleware:
    async def test_x_content_type_options(self, app_with_headers):
        transport = ASGITransport(app=app_with_headers)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/test")
            assert r.headers["x-content-type-options"] == "nosniff"

    async def test_x_frame_options(self, app_with_headers):
        transport = ASGITransport(app=app_with_headers)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/test")
            assert r.headers["x-frame-options"] == "DENY"

    async def test_referrer_policy(self, app_with_headers):
        transport = ASGITransport(app=app_with_headers)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/test")
            assert r.headers["referrer-policy"] == "strict-origin-when-cross-origin"

    async def test_permissions_policy(self, app_with_headers):
        transport = ASGITransport(app=app_with_headers)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/test")
            assert r.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"

    async def test_content_security_policy(self, app_with_headers):
        """SEC-007: CSP header must be present."""
        transport = ASGITransport(app=app_with_headers)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/test")
            assert "content-security-policy" in r.headers
            assert "default-src" in r.headers["content-security-policy"]

    async def test_strict_transport_security(self, app_with_headers):
        """SEC-007: HSTS header must be present with preload."""
        transport = ASGITransport(app=app_with_headers)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/test")
            hsts = r.headers["strict-transport-security"]
            assert "max-age" in hsts
            assert "preload" in hsts
