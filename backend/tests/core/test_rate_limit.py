"""Tests for rate limiting."""

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI, Request
from unittest.mock import MagicMock

from app.core.rate_limit import get_client_ip, limiter, rate_limit_handler
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


class TestGetClientIp:
    """SEC-004: Test proxy-aware IP extraction."""

    def _make_request(self, headers=None, client_host="127.0.0.1"):
        request = MagicMock(spec=Request)
        request.headers = headers or {}
        request.client = MagicMock()
        request.client.host = client_host
        return request

    def test_uses_x_forwarded_for_when_present(self):
        request = self._make_request(
            headers={"x-forwarded-for": "203.0.113.50, 70.41.3.18, 150.172.238.178"}
        )
        assert get_client_ip(request) == "203.0.113.50"

    def test_falls_back_to_client_host(self):
        request = self._make_request(client_host="192.168.1.100")
        assert get_client_ip(request) == "192.168.1.100"

    def test_single_ip_in_forwarded_for(self):
        request = self._make_request(headers={"x-forwarded-for": "10.0.0.1"})
        assert get_client_ip(request) == "10.0.0.1"

    def test_strips_whitespace_from_ip(self):
        request = self._make_request(
            headers={"x-forwarded-for": "  203.0.113.50 , 70.41.3.18"}
        )
        assert get_client_ip(request) == "203.0.113.50"

    def test_empty_forwarded_for_falls_back(self):
        request = self._make_request(
            headers={"x-forwarded-for": ""}, client_host="10.10.10.10"
        )
        assert get_client_ip(request) == "10.10.10.10"


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
