"""Tests for billing routes."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.billing.routes import router, webhook_router
from app.core.auth import get_current_user_id
from fastapi import FastAPI
from tests.helpers import mock_settings_with_cors

app = FastAPI()
app.include_router(router, prefix="/api/v1")
app.include_router(webhook_router)


async def _override_auth() -> str:
    return "user-1"


app.dependency_overrides[get_current_user_id] = _override_auth


@pytest.fixture
def client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestCheckoutRoute:
    @patch("app.core.url_validation.get_settings")
    async def test_returns_session_url(self, mock_gs: MagicMock, client):
        mock_gs.return_value = mock_settings_with_cors("https://example.com")
        with patch(
            "app.billing.service.create_checkout_session",
            new_callable=AsyncMock,
            return_value="https://checkout.stripe.com/session_123",
        ):
            response = await client.post(
                "/api/v1/billing/checkout",
                json={
                    "price_id": "price_abc",
                    "success_url": "https://example.com/success",
                    "cancel_url": "https://example.com/cancel",
                },
                headers={"x-user-id": "user_1"},
            )

            assert response.status_code == 200
            assert response.json() == {"url": "https://checkout.stripe.com/session_123"}


class TestPortalRoute:
    @patch("app.core.url_validation.get_settings")
    async def test_returns_portal_url(self, mock_gs: MagicMock, client):
        mock_gs.return_value = mock_settings_with_cors("https://example.com")
        with patch(
            "app.billing.service.create_portal_session",
            new_callable=AsyncMock,
            return_value="https://billing.stripe.com/portal_123",
        ) as mock_portal:
            response = await client.post(
                "/api/v1/billing/portal",
                json={
                    "return_url": "https://example.com/dashboard",
                    "customer_id": "cus_abc123",
                },
            )

            assert response.status_code == 200
            assert response.json() == {"url": "https://billing.stripe.com/portal_123"}
            mock_portal.assert_called_once_with(
                "cus_abc123", "https://example.com/dashboard"
            )

    async def test_requires_customer_id_in_body(self, client):
        """Portal requires customer_id in the request body, not a header."""
        response = await client.post(
            "/api/v1/billing/portal",
            json={"return_url": "https://example.com/dashboard"},
        )
        assert response.status_code == 422


class TestWebhookRoute:
    async def test_processes_valid_webhook(self, client):
        with patch(
            "app.billing.service.handle_webhook",
            new_callable=AsyncMock,
            return_value={"handled": True, "type": "checkout.session.completed"},
        ):
            response = await client.post(
                "/webhooks/stripe",
                content=b'{"type": "checkout.session.completed"}',
                headers={
                    "stripe-signature": "t=123,v1=abc",
                    "content-type": "application/json",
                },
            )

            assert response.status_code == 200
            assert response.json()["handled"] is True
