"""Tests for billing routes."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.billing.routes import router, webhook_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix="/api/v1")
app.include_router(webhook_router)


@pytest.fixture
def client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestCheckoutRoute:
    async def test_returns_session_url(self, client):
        with patch(
            "app.billing.service.create_checkout_session",
            new_callable=AsyncMock,
            return_value="https://checkout.stripe.com/session_123",
        ):
            response = await client.post(
                "/api/v1/billing/checkout",
                json={"price_id": "price_abc"},
                headers={"x-user-id": "user_1"},
            )

            assert response.status_code == 200
            assert response.json() == {"url": "https://checkout.stripe.com/session_123"}

    async def test_requires_user_id_header(self, client):
        response = await client.post(
            "/api/v1/billing/checkout",
            json={"price_id": "price_abc"},
        )
        assert response.status_code == 422


class TestPortalRoute:
    async def test_returns_portal_url(self, client):
        with patch(
            "app.billing.service.create_portal_session",
            new_callable=AsyncMock,
            return_value="https://billing.stripe.com/portal_123",
        ):
            response = await client.post(
                "/api/v1/billing/portal",
                json={"return_url": "https://example.com/dashboard"},
                headers={"x-customer-id": "cus_abc123"},
            )

            assert response.status_code == 200
            assert response.json() == {"url": "https://billing.stripe.com/portal_123"}

    async def test_requires_customer_id_header(self, client):
        response = await client.post(
            "/api/v1/billing/portal",
            json={},
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
