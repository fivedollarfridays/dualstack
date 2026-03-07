"""Tests for app.health.checks module."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from app.health.checks import (
    router,
    check_database,
)


@pytest.fixture
def health_app():
    """Create a FastAPI app with the health router."""
    app = FastAPI()
    app.include_router(router)
    return app



class TestCheckDatabase:
    """Test check_database function."""

    @pytest.mark.asyncio
    async def test_database_up(self):
        """Should return status 'up' when database is accessible."""
        mock_conn = AsyncMock()
        mock_engine = MagicMock()
        mock_engine.connect = MagicMock(return_value=AsyncMock())
        mock_engine.connect.return_value.__aenter__ = AsyncMock(
            return_value=mock_conn
        )
        mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("app.health.checks.get_engine", return_value=mock_engine):
            result = await check_database()
            assert result.name == "database"
            assert result.status == "up"

    @pytest.mark.asyncio
    async def test_database_down(self):
        """Should return status 'down' with generic error, not leak details."""
        mock_engine = MagicMock()
        mock_engine.connect = MagicMock(side_effect=Exception("Connection refused"))

        with patch("app.health.checks.get_engine", return_value=mock_engine):
            result = await check_database()
            assert result.name == "database"
            assert result.status == "down"
            assert result.error == "database unavailable"
            assert "Connection refused" not in (result.error or "")


class TestLivenessEndpoint:
    """Test GET /health/live endpoint."""

    @pytest.mark.asyncio
    async def test_returns_alive(self, health_app):
        """Should return alive=true."""
        transport = ASGITransport(app=health_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health/live")
            assert response.status_code == 200
            data = response.json()
            assert data["alive"] is True

    @pytest.mark.asyncio
    async def test_does_not_expose_uptime(self, health_app):
        """NEW-005: /health/live should not expose uptime_seconds."""
        transport = ASGITransport(app=health_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health/live")
            data = response.json()
            assert "uptime_seconds" not in data


class TestReadinessEndpoint:
    """Test GET /health/ready endpoint."""

    @pytest.mark.asyncio
    async def test_does_not_expose_latency(self, health_app):
        """NEW-005: /health/ready should not expose latency_ms."""
        from app.health.models import ServiceCheck

        mock_check = ServiceCheck(name="database", status="up")
        with patch("app.health.checks.check_database", return_value=mock_check):
            transport = ASGITransport(app=health_app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/health/ready")
                data = response.json()
                for check in data["checks"]:
                    assert "latency_ms" not in check

    @pytest.mark.asyncio
    async def test_ready_when_db_up(self, health_app):
        """Should return ready=true when database is up."""
        from app.health.models import ServiceCheck

        mock_check = ServiceCheck(name="database", status="up")
        with patch("app.health.checks.check_database", return_value=mock_check):
            transport = ASGITransport(app=health_app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/health/ready")
                assert response.status_code == 200
                data = response.json()
                assert data["ready"] is True

    @pytest.mark.asyncio
    async def test_not_ready_when_db_down(self, health_app):
        """Should return 503 and ready=false when database is down."""
        from app.health.models import ServiceCheck

        mock_check = ServiceCheck(
            name="database", status="down", error="Connection refused"
        )
        with patch("app.health.checks.check_database", return_value=mock_check):
            transport = ASGITransport(app=health_app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/health/ready")
                assert response.status_code == 503
                data = response.json()
                assert data["ready"] is False


class TestHealthEndpoint:
    """Test GET /health endpoint."""

    @pytest.mark.asyncio
    async def test_healthy_status(self, health_app):
        """Should return status 'healthy' when DB is up."""
        from app.health.models import ServiceCheck

        mock_check = ServiceCheck(name="database", status="up")
        with patch("app.health.checks.check_database", return_value=mock_check):
            transport = ASGITransport(app=health_app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_does_not_expose_version_or_uptime(self, health_app):
        """SEC-011: /health should not expose version or uptime."""
        from app.health.models import ServiceCheck

        mock_check = ServiceCheck(name="database", status="up")
        with patch("app.health.checks.check_database", return_value=mock_check):
            transport = ASGITransport(app=health_app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/health")
                data = response.json()
                assert "version" not in data
                assert "uptime_seconds" not in data

    @pytest.mark.asyncio
    async def test_degraded_status(self, health_app):
        """Should return status 'degraded' when DB is down."""
        from app.health.models import ServiceCheck

        mock_check = ServiceCheck(
            name="database", status="down", error="Connection refused"
        )
        with patch("app.health.checks.check_database", return_value=mock_check):
            transport = ASGITransport(app=health_app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_unhealthy_status(self, health_app):
        """Should return status 'unhealthy' when check_database raises."""
        with patch(
            "app.health.checks.check_database",
            side_effect=Exception("total failure"),
        ):
            transport = ASGITransport(app=health_app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.get("/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "unhealthy"
