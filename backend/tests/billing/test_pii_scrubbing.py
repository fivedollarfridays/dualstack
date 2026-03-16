"""Tests for webhook PII scrubbing."""

from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.billing import service
from app.billing.pii import scrub_pii


class TestScrubPiiCustomerFields:
    """Verify customer PII fields are stripped from webhook event data."""

    def test_strips_customer_email(self) -> None:
        event_data = {
            "id": "cs_123",
            "customer": "cus_abc",
            "customer_email": "user@example.com",
        }
        result = scrub_pii(event_data)
        assert "customer_email" not in result

    def test_strips_customer_name(self) -> None:
        event_data = {
            "id": "cs_123",
            "customer_details": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "address": {"line1": "123 Main St", "city": "NYC"},
            },
        }
        result = scrub_pii(event_data)
        details = result.get("customer_details", {})
        assert details.get("name") == "[REDACTED]"
        assert details.get("email") == "[REDACTED]"
        assert details.get("phone") == "[REDACTED]"
        assert details.get("address") == "[REDACTED]"

    def test_preserves_customer_id(self) -> None:
        event_data = {
            "id": "cs_123",
            "customer": "cus_abc",
            "customer_email": "user@example.com",
        }
        result = scrub_pii(event_data)
        assert result["customer"] == "cus_abc"

    def test_preserves_subscription_id(self) -> None:
        event_data = {
            "id": "sub_456",
            "status": "active",
            "customer": "cus_abc",
        }
        result = scrub_pii(event_data)
        assert result["id"] == "sub_456"
        assert result["status"] == "active"


class TestScrubPiiNestedFields:
    """Verify PII is stripped from nested billing/charge objects."""

    def test_strips_billing_details(self) -> None:
        event_data = {
            "id": "ch_123",
            "billing_details": {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+1987654321",
                "address": {
                    "line1": "456 Oak Ave",
                    "city": "LA",
                    "state": "CA",
                    "postal_code": "90001",
                    "country": "US",
                },
            },
        }
        result = scrub_pii(event_data)
        bd = result["billing_details"]
        assert bd["name"] == "[REDACTED]"
        assert bd["email"] == "[REDACTED]"
        assert bd["phone"] == "[REDACTED]"
        assert bd["address"] == "[REDACTED]"

    def test_strips_charges_billing_details(self) -> None:
        event_data = {
            "id": "in_123",
            "charges": {
                "data": [
                    {
                        "id": "ch_1",
                        "billing_details": {
                            "name": "Bob",
                            "email": "bob@example.com",
                        },
                    }
                ]
            },
        }
        result = scrub_pii(event_data)
        charge = result["charges"]["data"][0]
        assert charge["id"] == "ch_1"
        assert charge["billing_details"]["name"] == "[REDACTED]"
        assert charge["billing_details"]["email"] == "[REDACTED]"

    def test_strips_shipping_details(self) -> None:
        event_data = {
            "id": "cs_123",
            "shipping": {
                "name": "Alice",
                "phone": "+1111111111",
                "address": {"line1": "789 Pine St"},
            },
        }
        result = scrub_pii(event_data)
        shipping = result["shipping"]
        assert shipping["name"] == "[REDACTED]"
        assert shipping["phone"] == "[REDACTED]"
        assert shipping["address"] == "[REDACTED]"

    def test_does_not_mutate_original(self) -> None:
        event_data = {
            "id": "cs_123",
            "customer_email": "user@example.com",
            "billing_details": {"name": "John"},
        }
        scrub_pii(event_data)
        assert event_data["customer_email"] == "user@example.com"
        assert event_data["billing_details"]["name"] == "John"

    def test_handles_missing_nested_objects(self) -> None:
        event_data = {"id": "cs_123", "status": "complete"}
        result = scrub_pii(event_data)
        assert result == {"id": "cs_123", "status": "complete"}


@contextmanager
def _mock_webhook_handlers():
    """Replace _WEBHOOK_HANDLERS with async no-ops."""
    noop_handlers = {
        "checkout.session.completed": AsyncMock(),
    }
    with patch.dict("app.billing.service._WEBHOOK_HANDLERS", noop_handlers):
        yield


class TestScrubPiiIntegration:
    """Verify scrub_pii is called in webhook handling flow."""

    @patch("app.billing.service.get_settings")
    async def test_webhook_debug_log_uses_scrubbed_data(
        self, mock_get_settings: MagicMock
    ) -> None:
        """Webhook handler should log scrubbed data, not raw PII."""
        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_123",
                    "customer": "cus_abc",
                    "customer_email": "secret@example.com",
                }
            },
        }

        with (
            patch("stripe.Webhook.construct_event", return_value=event),
            patch("app.billing.service.logger") as mock_logger,
            _mock_webhook_handlers(),
        ):
            await service.handle_webhook(b"payload", "sig_header", db=MagicMock())
            # Debug log should have been called with scrubbed data
            mock_logger.debug.assert_called_once()
            logged_data = mock_logger.debug.call_args[0][2]
            assert "customer_email" not in logged_data
            assert logged_data["customer"] == "cus_abc"

    @patch("app.billing.service.get_settings")
    async def test_webhook_error_log_uses_scrubbed_data(
        self, mock_get_settings: MagicMock
    ) -> None:
        """Webhook handler errors should log scrubbed data, not raw PII."""
        settings = MagicMock()
        settings.stripe_webhook_secret = "whsec_test_fake"
        mock_get_settings.return_value = settings

        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_err",
                    "customer_email": "secret@example.com",
                    "billing_details": {"name": "Jane", "email": "jane@ex.com"},
                }
            },
        }

        error_handlers = {
            "checkout.session.completed": AsyncMock(
                side_effect=RuntimeError("db error")
            ),
        }
        with (
            patch("stripe.Webhook.construct_event", return_value=event),
            patch("app.billing.service.logger") as mock_logger,
            patch.dict("app.billing.service._WEBHOOK_HANDLERS", error_handlers),
        ):
            with pytest.raises(RuntimeError, match="db error"):
                await service.handle_webhook(
                    b"payload", "sig_header", db=MagicMock()
                )
            mock_logger.exception.assert_called_once()
            logged_data = mock_logger.exception.call_args[0][2]
            assert "customer_email" not in logged_data
            assert logged_data["billing_details"]["name"] == "[REDACTED]"
