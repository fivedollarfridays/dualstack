"""Tests for billing routes."""

from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

import pytest
from httpx import ASGITransport, AsyncClient

from app.billing.routes import router, webhook_router
from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.core.exception_handlers import register_exception_handlers
from fastapi import FastAPI
from tests.helpers import mock_settings_with_cors

app = FastAPI()
register_exception_handlers(app)
app.include_router(router, prefix="/api/v1")
app.include_router(webhook_router)


async def _override_auth() -> str:
    return "user-1"


async def _override_db():
    yield MagicMock(spec=AsyncSession)


app.dependency_overrides[get_current_user_id] = _override_auth
app.dependency_overrides[get_db] = _override_db


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
    async def test_returns_404_when_no_billing_account(
        self, mock_gs: MagicMock, client
    ):
        """Portal returns 404 when user has no billing account."""
        mock_gs.return_value = mock_settings_with_cors("https://example.com")
        with patch(
            "app.billing.routes.get_user_by_clerk_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await client.post(
                "/api/v1/billing/portal",
                json={"return_url": "https://example.com/dashboard"},
            )
        assert response.status_code == 404
        body = response.json()
        assert body["error"]["code"] == "NOT_FOUND"
        assert "subscribe" in body["error"]["message"].lower()

    def test_portal_has_rate_limit_decorator(self):
        """NEW-011: /billing/portal should have a rate limit decorator."""
        from app.billing.routes import create_portal

        # slowapi wraps the function, setting __wrapped__
        assert hasattr(create_portal, "__wrapped__"), (
            "create_portal should have rate limit decorator"
        )


class TestCheckoutAuditEvent:
    """NEW-006: Checkout should emit audit event (persisted to DB)."""

    @patch("app.core.url_validation.get_settings")
    async def test_checkout_emits_audit(self, mock_gs: MagicMock, client):
        mock_gs.return_value = mock_settings_with_cors("https://example.com")
        with (
            patch(
                "app.billing.service.create_checkout_session",
                new_callable=AsyncMock,
                return_value="https://checkout.stripe.com/session_123",
            ),
            patch(
                "app.billing.routes.persist_audit_event", new_callable=AsyncMock
            ) as mock_audit,
        ):
            await client.post(
                "/api/v1/billing/checkout",
                json={
                    "price_id": "price_abc",
                    "success_url": "https://example.com/success",
                    "cancel_url": "https://example.com/cancel",
                },
                headers={"x-user-id": "user_1"},
            )
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs["action"] == "billing.checkout"
            assert kwargs["user_id"] == "user-1"
            assert kwargs["resource_type"] == "checkout"


class TestWebhookRoute:
    async def test_processes_valid_webhook(self, client):
        with (
            patch("app.billing.routes.get_settings") as mock_gs,
            patch(
                "app.billing.service.handle_webhook",
                new_callable=AsyncMock,
                return_value={"handled": True, "type": "checkout.session.completed"},
            ),
        ):
            settings = MagicMock()
            settings.stripe_webhook_secret = "whsec_test"
            mock_gs.return_value = settings

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

    async def test_returns_503_when_secret_not_configured(self, client):
        """AUDIT-001: Webhook returns 503 when stripe_webhook_secret is empty."""
        with patch("app.billing.routes.get_settings") as mock_gs:
            settings = MagicMock()
            settings.stripe_webhook_secret = ""
            mock_gs.return_value = settings

            response = await client.post(
                "/webhooks/stripe",
                content=b'{"type": "checkout.session.completed"}',
                headers={
                    "stripe-signature": "t=123,v1=abc",
                    "content-type": "application/json",
                },
            )

            assert response.status_code == 503
            body = response.json()
            assert body["error"]["code"] == "WEBHOOK_NOT_CONFIGURED"
