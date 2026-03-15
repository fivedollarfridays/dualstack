"""Tests for metrics endpoint authentication (S-4)."""

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI
from unittest.mock import patch

from app.core.config import Settings
from app.core.exception_handlers import register_exception_handlers
from app.core.metrics_routes import router


def _create_metrics_app() -> FastAPI:
    """Create a minimal FastAPI app with the metrics router."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    return app


class TestMetricsAuth:
    """Test /metrics endpoint access control via X-Metrics-Key header."""

    async def test_accessible_when_no_key_configured(self):
        """When metrics_api_key is empty, /metrics should be accessible."""
        settings = Settings(metrics_api_key="")
        with patch("app.core.metrics_routes.get_settings", return_value=settings):
            app = _create_metrics_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                response = await c.get("/metrics")
                assert response.status_code == 200

    async def test_blocked_with_wrong_key(self):
        """When metrics_api_key is set, wrong key should return 403."""
        settings = Settings(metrics_api_key="secret-key-12345678")
        with patch("app.core.metrics_routes.get_settings", return_value=settings):
            app = _create_metrics_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                response = await c.get(
                    "/metrics", headers={"X-Metrics-Key": "wrong-key"}
                )
                assert response.status_code == 403
                body = response.json()
                assert body["error"]["code"] == "AUTHORIZATION_ERROR"
                assert "metrics" in body["error"]["message"].lower()

    async def test_blocked_with_no_key_header(self):
        """When metrics_api_key is set, missing header should return 403."""
        settings = Settings(metrics_api_key="secret-key-12345678")
        with patch("app.core.metrics_routes.get_settings", return_value=settings):
            app = _create_metrics_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                response = await c.get("/metrics")
                assert response.status_code == 403
                body = response.json()
                assert body["error"]["code"] == "AUTHORIZATION_ERROR"

    async def test_accessible_with_correct_key(self):
        """When metrics_api_key is set, correct key should return 200."""
        settings = Settings(metrics_api_key="secret-key-12345678")
        with patch("app.core.metrics_routes.get_settings", return_value=settings):
            app = _create_metrics_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                response = await c.get(
                    "/metrics", headers={"X-Metrics-Key": "secret-key-12345678"}
                )
                assert response.status_code == 200
