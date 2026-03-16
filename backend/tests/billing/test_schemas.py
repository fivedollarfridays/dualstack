"""Tests for billing schemas."""

from unittest.mock import MagicMock, patch

import pytest

from app.billing.schemas import CheckoutRequest, PortalRequest, WebhookPayload
from tests.helpers import mock_settings_with_cors


class TestCheckoutRequest:
    @patch("app.core.url_validation.get_settings")
    def test_valid_with_all_fields(self, mock_gs: MagicMock) -> None:
        mock_gs.return_value = mock_settings_with_cors("https://example.com")
        req = CheckoutRequest(
            price_id="price_abc123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )
        assert req.price_id == "price_abc123"
        assert req.success_url == "https://example.com/success"
        assert req.cancel_url == "https://example.com/cancel"

    def test_price_id_required(self) -> None:
        with pytest.raises(Exception):
            CheckoutRequest()  # type: ignore[call-arg]

    def test_success_url_required(self) -> None:
        with pytest.raises(Exception):
            CheckoutRequest(price_id="price_abc123", cancel_url="https://x.com")  # type: ignore[call-arg]

    @patch("app.core.url_validation.get_settings")
    def test_rejects_foreign_success_url(self, mock_gs: MagicMock) -> None:
        mock_gs.return_value = mock_settings_with_cors("https://myapp.com")
        with pytest.raises(ValueError, match="URL origin is not allowed"):
            CheckoutRequest(
                price_id="price_abc",
                success_url="https://evil.com/phish",
                cancel_url="https://myapp.com/cancel",
            )

    @patch("app.core.url_validation.get_settings")
    def test_rejects_foreign_cancel_url(self, mock_gs: MagicMock) -> None:
        mock_gs.return_value = mock_settings_with_cors("https://myapp.com")
        with pytest.raises(ValueError, match="URL origin is not allowed"):
            CheckoutRequest(
                price_id="price_abc",
                success_url="https://myapp.com/success",
                cancel_url="https://evil.com/cancel",
            )

    @patch("app.core.url_validation.get_settings")
    def test_rejects_invalid_price_id(self, mock_gs: MagicMock) -> None:
        mock_gs.return_value = mock_settings_with_cors("https://example.com")
        with pytest.raises(ValueError, match="Invalid Stripe price ID format"):
            CheckoutRequest(
                price_id="invalid_id",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

    @patch("app.core.url_validation.get_settings")
    def test_rejects_price_id_with_special_chars(self, mock_gs: MagicMock) -> None:
        mock_gs.return_value = mock_settings_with_cors("https://example.com")
        with pytest.raises(ValueError, match="Invalid Stripe price ID format"):
            CheckoutRequest(
                price_id="price_abc-123",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

    @patch("app.core.url_validation.get_settings")
    def test_rejects_empty_price_id_suffix(self, mock_gs: MagicMock) -> None:
        mock_gs.return_value = mock_settings_with_cors("https://example.com")
        with pytest.raises(ValueError, match="Invalid Stripe price ID format"):
            CheckoutRequest(
                price_id="price_",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )


class TestPortalRequest:
    @patch("app.core.url_validation.get_settings")
    def test_valid_with_return_url(self, mock_gs: MagicMock) -> None:
        mock_gs.return_value = mock_settings_with_cors("https://example.com")
        req = PortalRequest(
            return_url="https://example.com/dashboard",
        )
        assert req.return_url == "https://example.com/dashboard"

    def test_return_url_required(self) -> None:
        with pytest.raises(Exception):
            PortalRequest()  # type: ignore[call-arg]

    def test_does_not_accept_customer_id(self) -> None:
        """NEW-007: PortalRequest must not accept customer_id from client input."""
        assert (
            not hasattr(PortalRequest.model_fields, "customer_id")
            or "customer_id" not in PortalRequest.model_fields
        )

    @patch("app.core.url_validation.get_settings")
    def test_rejects_foreign_return_url(self, mock_gs: MagicMock) -> None:
        mock_gs.return_value = mock_settings_with_cors("https://myapp.com")
        with pytest.raises(ValueError, match="URL origin is not allowed"):
            PortalRequest(
                return_url="https://evil.com/dashboard",
            )


class TestWebhookPayload:
    def test_construction(self) -> None:
        payload = WebhookPayload(
            type="checkout.session.completed",
            data={"object": {"id": "cs_123", "metadata": {"user_id": "user_1"}}},
        )
        assert payload.type == "checkout.session.completed"
        assert payload.data["object"]["id"] == "cs_123"

    def test_minimal_data(self) -> None:
        payload = WebhookPayload(type="some.event", data={})
        assert payload.type == "some.event"
        assert payload.data == {}
