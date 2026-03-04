"""Tests for billing schemas."""

from app.billing.schemas import CheckoutRequest, PortalRequest, WebhookPayload


class TestCheckoutRequest:
    def test_valid_with_all_fields(self):
        req = CheckoutRequest(
            price_id="price_abc123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )
        assert req.price_id == "price_abc123"
        assert req.success_url == "https://example.com/success"
        assert req.cancel_url == "https://example.com/cancel"

    def test_defaults_for_urls(self):
        req = CheckoutRequest(price_id="price_abc123")
        assert req.success_url == "http://localhost:3000/dashboard?checkout=success"
        assert req.cancel_url == "http://localhost:3000/dashboard?checkout=cancel"

    def test_price_id_required(self):
        import pytest

        with pytest.raises(Exception):
            CheckoutRequest()  # type: ignore[call-arg]


class TestPortalRequest:
    def test_valid_with_return_url(self):
        req = PortalRequest(return_url="https://example.com/dashboard")
        assert req.return_url == "https://example.com/dashboard"

    def test_default_return_url(self):
        req = PortalRequest()
        assert req.return_url == "http://localhost:3000/dashboard"


class TestWebhookPayload:
    def test_construction(self):
        payload = WebhookPayload(
            type="checkout.session.completed",
            data={"object": {"id": "cs_123", "metadata": {"user_id": "user_1"}}},
        )
        assert payload.type == "checkout.session.completed"
        assert payload.data["object"]["id"] == "cs_123"

    def test_minimal_data(self):
        payload = WebhookPayload(type="some.event", data={})
        assert payload.type == "some.event"
        assert payload.data == {}
