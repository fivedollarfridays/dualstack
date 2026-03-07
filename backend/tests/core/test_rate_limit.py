"""Tests for rate limiting."""

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI, Request

from app.core.rate_limit import limiter, rate_limit_handler
from slowapi.errors import RateLimitExceeded


@pytest.fixture
def rate_limited_app():
    """Create a test app with a strict rate limit for testing."""
    app = FastAPI()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

    @app.get("/limited")
    @limiter.limit("2/minute")
    async def limited_route(request: Request):
        return {"ok": True}

    @app.get("/unlimited")
    async def unlimited_route():
        return {"ok": True}

    return app


class TestRateLimiting:
    async def test_allows_requests_under_limit(self, rate_limited_app):
        transport = ASGITransport(app=rate_limited_app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/limited")
            assert r.status_code == 200

    async def test_returns_429_when_limit_exceeded(self, rate_limited_app):
        transport = ASGITransport(app=rate_limited_app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            # Make requests up to the limit
            await c.get("/limited")
            await c.get("/limited")
            # Third request should be rate limited
            r = await c.get("/limited")
            assert r.status_code == 429

    async def test_returns_rate_limit_error_format(self, rate_limited_app):
        transport = ASGITransport(app=rate_limited_app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            await c.get("/limited")
            await c.get("/limited")
            r = await c.get("/limited")
            body = r.json()
            assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    async def test_unlimited_routes_not_affected(self, rate_limited_app):
        transport = ASGITransport(app=rate_limited_app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            for _ in range(5):
                r = await c.get("/unlimited")
                assert r.status_code == 200
