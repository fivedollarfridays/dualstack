"""Tests for app.main module."""

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
    async def test_lifespan_yields(self):
        """Lifespan context manager should yield without error."""
        from fastapi import FastAPI

        test_app = FastAPI()
        async with lifespan(test_app):
            pass  # Startup and shutdown should work
