"""Tests for billing response schemas (T25.5)."""

import pytest
from pydantic import ValidationError


class TestCheckoutResponse:
    def test_valid_url(self) -> None:
        from app.billing.schemas import CheckoutResponse

        resp = CheckoutResponse(url="https://checkout.stripe.com/abc")
        assert resp.url == "https://checkout.stripe.com/abc"

    def test_url_required(self) -> None:
        from app.billing.schemas import CheckoutResponse

        with pytest.raises(ValidationError):
            CheckoutResponse()  # type: ignore[call-arg]


class TestPortalResponse:
    def test_valid_url(self) -> None:
        from app.billing.schemas import PortalResponse

        resp = PortalResponse(url="https://billing.stripe.com/session/xyz")
        assert resp.url == "https://billing.stripe.com/session/xyz"

    def test_url_required(self) -> None:
        from app.billing.schemas import PortalResponse

        with pytest.raises(ValidationError):
            PortalResponse()  # type: ignore[call-arg]


class TestWebhookResponse:
    def test_handled_true(self) -> None:
        from app.billing.schemas import WebhookResponse

        resp = WebhookResponse(handled=True, type="checkout.session.completed")
        assert resp.handled is True
        assert resp.type == "checkout.session.completed"

    def test_handled_false(self) -> None:
        from app.billing.schemas import WebhookResponse

        resp = WebhookResponse(handled=False, type="unknown.event")
        assert resp.handled is False
        assert resp.type == "unknown.event"

    def test_both_fields_required(self) -> None:
        from app.billing.schemas import WebhookResponse

        with pytest.raises(ValidationError):
            WebhookResponse()  # type: ignore[call-arg]

        with pytest.raises(ValidationError):
            WebhookResponse(handled=True)  # type: ignore[call-arg]

        with pytest.raises(ValidationError):
            WebhookResponse(type="event")  # type: ignore[call-arg]
