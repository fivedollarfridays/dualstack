"""Tests for billing service."""

from unittest.mock import MagicMock, patch

import pytest

from app.billing import service


@pytest.fixture
def mock_settings():
    """Mock settings with Stripe keys."""
    settings = MagicMock()
    settings.stripe_secret_key = "sk_test_fake"
    settings.stripe_webhook_secret = "whsec_test_fake"
    return settings


class TestCreateCheckoutSession:
    @patch("app.billing.service.get_settings")
    async def test_returns_session_url(self, mock_get_settings, mock_settings):
        mock_get_settings.return_value = mock_settings

        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/session_123"

        with patch("stripe.checkout.Session.create", return_value=mock_session) as mock_create:
            url = await service.create_checkout_session(
                user_id="user_1",
                price_id="price_abc",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

            assert url == "https://checkout.stripe.com/session_123"
            mock_create.assert_called_once_with(
                mode="subscription",
                customer_email=None,
                metadata={"user_id": "user_1"},
                line_items=[{"price": "price_abc", "quantity": 1}],
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )


class TestCreatePortalSession:
    @patch("app.billing.service.get_settings")
    async def test_returns_portal_url(self, mock_get_settings, mock_settings):
        mock_get_settings.return_value = mock_settings

        mock_session = MagicMock()
        mock_session.url = "https://billing.stripe.com/portal_123"

        with patch(
            "stripe.billing_portal.Session.create", return_value=mock_session
        ) as mock_create:
            url = await service.create_portal_session(
                customer_id="cus_abc123",
                return_url="https://example.com/dashboard",
            )

            assert url == "https://billing.stripe.com/portal_123"
            mock_create.assert_called_once_with(
                customer="cus_abc123",
                return_url="https://example.com/dashboard",
            )


class TestHandleWebhook:
    @patch("app.billing.service.get_settings")
    async def test_handles_checkout_completed(self, mock_get_settings, mock_settings):
        mock_get_settings.return_value = mock_settings

        event = {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_123", "metadata": {"user_id": "user_1"}}},
        }

        with patch("stripe.Webhook.construct_event", return_value=event):
            result = await service.handle_webhook(b"payload", "sig_header")

            assert result["handled"] is True
            assert result["type"] == "checkout.session.completed"

    @patch("app.billing.service.get_settings")
    async def test_handles_subscription_updated(self, mock_get_settings, mock_settings):
        mock_get_settings.return_value = mock_settings

        event = {
            "type": "customer.subscription.updated",
            "data": {"object": {"id": "sub_123", "status": "active"}},
        }

        with patch("stripe.Webhook.construct_event", return_value=event):
            result = await service.handle_webhook(b"payload", "sig_header")

            assert result["handled"] is True
            assert result["type"] == "customer.subscription.updated"

    @patch("app.billing.service.get_settings")
    async def test_ignores_unknown_events(self, mock_get_settings, mock_settings):
        mock_get_settings.return_value = mock_settings

        event = {
            "type": "some.unknown.event",
            "data": {"object": {}},
        }

        with patch("stripe.Webhook.construct_event", return_value=event):
            result = await service.handle_webhook(b"payload", "sig_header")

            assert result["handled"] is False
            assert result["type"] == "some.unknown.event"
