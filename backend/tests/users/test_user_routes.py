"""Tests for user routes."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.auth import get_current_user_id
from app.core.exception_handlers import register_exception_handlers
from app.users.routes import router
from fastapi import FastAPI

app = FastAPI()
register_exception_handlers(app)
app.include_router(router, prefix="/api/v1")


async def _override_auth() -> str:
    return "clerk_user_123"


app.dependency_overrides[get_current_user_id] = _override_auth


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestGetCurrentUserRoute:
    async def test_returns_subscription_info_for_existing_user(self, client):
        """Authenticated user with subscription returns plan and status."""
        mock_user = AsyncMock()
        mock_user.subscription_plan = "pro"
        mock_user.subscription_status = "active"

        with patch(
            "app.users.routes.get_user_by_clerk_id",
            new_callable=AsyncMock,
            return_value=mock_user,
        ):
            response = await client.get("/api/v1/users/me")

        assert response.status_code == 200
        data = response.json()
        assert data["subscription_plan"] == "pro"
        assert data["subscription_status"] == "active"

    async def test_returns_free_defaults_for_unknown_user(self, client):
        """User not in database gets free plan defaults."""
        with patch(
            "app.users.routes.get_user_by_clerk_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await client.get("/api/v1/users/me")

        assert response.status_code == 200
        data = response.json()
        assert data["subscription_plan"] == "free"
        assert data["subscription_status"] == "none"

    async def test_returns_free_defaults_when_fields_are_none(self, client):
        """User with null subscription fields defaults to free."""
        mock_user = AsyncMock()
        mock_user.subscription_plan = None
        mock_user.subscription_status = None

        with patch(
            "app.users.routes.get_user_by_clerk_id",
            new_callable=AsyncMock,
            return_value=mock_user,
        ):
            response = await client.get("/api/v1/users/me")

        assert response.status_code == 200
        data = response.json()
        assert data["subscription_plan"] == "free"
        assert data["subscription_status"] == "none"

    async def test_does_not_expose_internal_fields(self, client):
        """Response must not include database id or stripe_customer_id."""
        mock_user = AsyncMock()
        mock_user.subscription_plan = "pro"
        mock_user.subscription_status = "active"

        with patch(
            "app.users.routes.get_user_by_clerk_id",
            new_callable=AsyncMock,
            return_value=mock_user,
        ):
            response = await client.get("/api/v1/users/me")

        data = response.json()
        assert "id" not in data
        assert "stripe_customer_id" not in data
        assert "clerk_user_id" not in data
