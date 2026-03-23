"""Tests for billing route response_model declarations (T25.5)."""

from typing import get_type_hints

from app.billing.routes import create_checkout, create_portal, stripe_webhook, router, webhook_router
from app.billing.schemas import CheckoutResponse, PortalResponse, WebhookResponse


class TestBillingRouteResponseModels:
    """Verify each billing route has response_model declared."""

    def _find_route(self, app_router, path: str, method: str = "POST"):
        """Find a route definition in the router."""
        for route in app_router.routes:
            if hasattr(route, "path") and route.path == path:
                if method in route.methods:
                    return route
        return None

    def test_checkout_has_response_model(self) -> None:
        route = self._find_route(router, "/billing/checkout")
        assert route is not None, "checkout route not found"
        assert route.response_model is CheckoutResponse

    def test_portal_has_response_model(self) -> None:
        route = self._find_route(router, "/billing/portal")
        assert route is not None, "portal route not found"
        assert route.response_model is PortalResponse

    def test_webhook_has_response_model(self) -> None:
        route = self._find_route(webhook_router, "/webhooks/stripe")
        assert route is not None, "webhook route not found"
        assert route.response_model is WebhookResponse


class TestBillingRouteReturnAnnotations:
    """Verify each billing route handler has a return type annotation."""

    def test_create_checkout_return_type(self) -> None:
        hints = get_type_hints(create_checkout)
        assert "return" in hints, "create_checkout missing return type annotation"
        assert hints["return"] is CheckoutResponse

    def test_create_portal_return_type(self) -> None:
        hints = get_type_hints(create_portal)
        assert "return" in hints, "create_portal missing return type annotation"
        assert hints["return"] is PortalResponse

    def test_stripe_webhook_return_type(self) -> None:
        hints = get_type_hints(stripe_webhook)
        assert "return" in hints, "stripe_webhook missing return type annotation"
        assert hints["return"] is WebhookResponse
