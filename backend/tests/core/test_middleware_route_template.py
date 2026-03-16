"""Tests for route template in Prometheus metrics (S-10)."""

import pytest
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from app.core.middleware import LoggingMiddleware


class TestRouteTemplateMetrics:
    """Test that Prometheus metrics use route templates, not raw paths."""

    @pytest.mark.asyncio
    async def test_metrics_use_route_template_not_raw_path(self):
        """Request to /items/some-uuid should record /items/{item_id} in metrics."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)

        @app.get("/items/{item_id}")
        async def get_item(item_id: str):
            return {"id": item_id}

        with (
            patch("app.core.middleware.increment_http_requests") as mock_inc,
            patch("app.core.middleware.observe_http_duration") as mock_obs,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                await client.get("/items/abc-123-uuid")

            # Metrics should use template path
            mock_inc.assert_called_once()
            call_kwargs = mock_inc.call_args.kwargs
            assert call_kwargs["endpoint"] == "/items/{item_id}"

            mock_obs.assert_called_once()
            obs_kwargs = mock_obs.call_args.kwargs
            assert obs_kwargs["endpoint"] == "/items/{item_id}"

    @pytest.mark.asyncio
    async def test_metrics_use_raw_path_when_no_route_matched(self):
        """Unmatched routes should fall back to raw path in metrics."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)

        @app.get("/ok")
        async def ok():
            return {"ok": True}

        with (
            patch("app.core.middleware.increment_http_requests") as mock_inc,
            patch("app.core.middleware.observe_http_duration"),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                # Request a path that doesn't match any route
                await client.get("/nonexistent")

            # For unmatched routes, raw path is used
            mock_inc.assert_called_once()
            call_kwargs = mock_inc.call_args.kwargs
            assert call_kwargs["endpoint"] == "/nonexistent"

    @pytest.mark.asyncio
    async def test_log_still_uses_raw_path(self):
        """Log lines should still contain the raw URL path for debugging."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)

        @app.get("/items/{item_id}")
        async def get_item(item_id: str):
            return {"id": item_id}

        with patch("app.core.middleware.logger") as mock_logger:
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                await client.get("/items/real-uuid-value")

            # request_started log should use raw path
            started_calls = [
                c
                for c in mock_logger.info.call_args_list
                if c.args and c.args[0] == "request_started"
            ]
            assert len(started_calls) >= 1
            assert started_calls[0].kwargs["path"] == "/items/real-uuid-value"
