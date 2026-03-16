"""Tests for billing service."""

from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import stripe

from app.billing import service


class TestCreateCheckoutSession:
    async def test_returns_session_url(self) -> None:
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/session_123"

        with patch(
            "stripe.checkout.Session.create", return_value=mock_session
        ) as mock_create:
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
    async def test_returns_portal_url(self) -> None:
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


@contextmanager
def _mock_webhook_handlers():
    """Replace _WEBHOOK_HANDLERS with async no-ops."""
    noop_handlers = {
        "checkout.session.completed": AsyncMock(),
        "customer.subscription.updated": AsyncMock(),
        "customer.subscription.deleted": AsyncMock(),
    }
    with patch.dict("app.billing.service._WEBHOOK_HANDLERS", noop_handlers):
        yield


class TestHandleWebhook:
    @patch("app.billing.service.get_settings")
    async def test_handles_checkout_completed(
        self, mock_get_settings: MagicMock
    ) -> None:
        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        event = {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_123", "metadata": {"user_id": "user_1"}}},
        }

        with (
            patch("stripe.Webhook.construct_event", return_value=event),
            _mock_webhook_handlers(),
        ):
            result = await service.handle_webhook(
                b"payload", "sig_header", db=MagicMock()
            )

            assert result["handled"] is True
            assert result["type"] == "checkout.session.completed"

    @patch("app.billing.service.get_settings")
    async def test_handles_subscription_updated(
        self, mock_get_settings: MagicMock
    ) -> None:
        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        event = {
            "type": "customer.subscription.updated",
            "data": {"object": {"id": "sub_123", "status": "active"}},
        }

        with (
            patch("stripe.Webhook.construct_event", return_value=event),
            _mock_webhook_handlers(),
        ):
            result = await service.handle_webhook(
                b"payload", "sig_header", db=MagicMock()
            )

            assert result["handled"] is True
            assert result["type"] == "customer.subscription.updated"

    @patch("app.billing.service.get_settings")
    async def test_handles_subscription_deleted(
        self, mock_get_settings: MagicMock
    ) -> None:
        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        event = {
            "type": "customer.subscription.deleted",
            "data": {"object": {"id": "sub_del_123", "status": "canceled"}},
        }

        with (
            patch("stripe.Webhook.construct_event", return_value=event),
            _mock_webhook_handlers(),
        ):
            result = await service.handle_webhook(
                b"payload", "sig_header", db=MagicMock()
            )

            assert result["handled"] is True
            assert result["type"] == "customer.subscription.deleted"

    @patch("app.billing.service.get_settings")
    async def test_ignores_unknown_events(self, mock_get_settings: MagicMock) -> None:
        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        event = {
            "type": "some.unknown.event",
            "data": {"object": {}},
        }

        with patch("stripe.Webhook.construct_event", return_value=event):
            result = await service.handle_webhook(
                b"payload", "sig_header", db=MagicMock()
            )

            assert result["handled"] is False
            assert result["type"] == "some.unknown.event"

    @patch("app.billing.service.get_settings")
    async def test_raises_on_invalid_signature(
        self, mock_get_settings: MagicMock
    ) -> None:
        """NEW-003: Invalid webhook signature should raise AuthenticationError."""
        from app.core.errors import AuthenticationError

        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        with patch(
            "stripe.Webhook.construct_event",
            side_effect=stripe.error.SignatureVerificationError(
                "bad sig", "sig_header"
            ),
        ):
            with pytest.raises(AuthenticationError):
                await service.handle_webhook(b"payload", "bad_sig", db=MagicMock())

    @patch("app.billing.service.get_settings")
    async def test_raises_on_malformed_payload(
        self, mock_get_settings: MagicMock
    ) -> None:
        """NEW-003: Malformed webhook payload should raise ValidationError."""
        from app.core.errors import ValidationError

        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        with patch(
            "stripe.Webhook.construct_event",
            side_effect=ValueError("Invalid payload"),
        ):
            with pytest.raises(ValidationError):
                await service.handle_webhook(
                    b"bad payload", "sig_header", db=MagicMock()
                )

    @patch("app.billing.service.get_settings")
    async def test_audit_log_on_signature_failure(
        self, mock_get_settings: MagicMock
    ) -> None:
        """NEW-003: Signature failure should emit an audit event."""
        from app.core.errors import AuthenticationError

        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        with (
            patch(
                "stripe.Webhook.construct_event",
                side_effect=stripe.error.SignatureVerificationError(
                    "bad sig", "sig_header"
                ),
            ),
            patch("app.billing.service.log_audit_event") as mock_audit,
        ):
            with pytest.raises(AuthenticationError):
                await service.handle_webhook(b"payload", "bad_sig", db=MagicMock())
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs["action"] == "webhook.signature_failure"

    @patch("app.billing.service.get_settings")
    async def test_audit_log_on_checkout_completed(
        self, mock_get_settings: MagicMock
    ) -> None:
        """AUDIT-008: Successful checkout.session.completed should be audit-logged."""
        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        event = {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_123", "metadata": {"user_id": "user_1"}}},
        }

        with (
            patch("stripe.Webhook.construct_event", return_value=event),
            patch("app.billing.service.log_audit_event") as mock_audit,
            _mock_webhook_handlers(),
        ):
            await service.handle_webhook(b"payload", "sig_header", db=MagicMock())
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs["action"] == "webhook.checkout_completed"
            assert kwargs["outcome"] == "success"
            assert kwargs["resource_id"] == "cs_123"

    @patch("app.billing.service.get_settings")
    async def test_audit_log_on_subscription_updated(
        self, mock_get_settings: MagicMock
    ) -> None:
        """AUDIT-008: Successful subscription.updated should be audit-logged."""
        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        event = {
            "type": "customer.subscription.updated",
            "data": {"object": {"id": "sub_456", "status": "active"}},
        }

        with (
            patch("stripe.Webhook.construct_event", return_value=event),
            patch("app.billing.service.log_audit_event") as mock_audit,
            _mock_webhook_handlers(),
        ):
            await service.handle_webhook(b"payload", "sig_header", db=MagicMock())
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs["action"] == "webhook.subscription_updated"
            assert kwargs["outcome"] == "success"
            assert kwargs["resource_id"] == "sub_456"

    @patch("app.billing.service.get_settings")
    async def test_no_audit_log_on_unhandled_event(
        self, mock_get_settings: MagicMock
    ) -> None:
        """AUDIT-008: Unhandled events should NOT be audit-logged."""
        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        event = {
            "type": "some.unknown.event",
            "data": {"object": {}},
        }

        with (
            patch("stripe.Webhook.construct_event", return_value=event),
            patch("app.billing.service.log_audit_event") as mock_audit,
        ):
            await service.handle_webhook(b"payload", "sig_header", db=MagicMock())
            mock_audit.assert_not_called()

    @patch("app.billing.service.get_settings")
    async def test_handler_error_reraises_with_failure_audit(
        self, mock_get_settings: MagicMock
    ) -> None:
        """Handler exceptions re-raise so Stripe retries, with failure audit."""
        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        event = {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_err", "metadata": {"user_id": "user_1"}}},
        }

        error_handlers = {
            "checkout.session.completed": AsyncMock(
                side_effect=RuntimeError("db error")
            ),
        }
        with (
            patch("stripe.Webhook.construct_event", return_value=event),
            patch("app.billing.service.log_audit_event") as mock_audit,
            patch.dict("app.billing.service._WEBHOOK_HANDLERS", error_handlers),
        ):
            with pytest.raises(RuntimeError, match="db error"):
                await service.handle_webhook(
                    b"payload", "sig_header", db=MagicMock()
                )
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs["outcome"] == "failure"
