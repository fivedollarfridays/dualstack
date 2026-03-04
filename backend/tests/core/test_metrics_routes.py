"""Tests for app.core.metrics_routes module."""

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from app.core.metrics_routes import router


@pytest.fixture
def metrics_app():
    """Create a minimal FastAPI app with the metrics router."""
    app = FastAPI()
    app.include_router(router)
    return app


class TestMetricsEndpoint:
    """Test GET /metrics endpoint."""

    @pytest.mark.asyncio
    async def test_returns_200(self, metrics_app):
        """GET /metrics should return 200."""
        transport = ASGITransport(app=metrics_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/metrics")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_returns_prometheus_content_type(self, metrics_app):
        """GET /metrics should return prometheus text format content type."""
        transport = ASGITransport(app=metrics_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/metrics")
            assert "text/plain" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_returns_metrics_content(self, metrics_app):
        """GET /metrics should return non-empty metrics data."""
        transport = ASGITransport(app=metrics_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/metrics")
            assert len(response.content) > 0
