"""Billing API routes."""

from fastapi import APIRouter, Header, Request

from app.billing import service
from app.billing.schemas import CheckoutRequest, PortalRequest

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout")
async def create_checkout(data: CheckoutRequest, x_user_id: str = Header()):
    """Create a Stripe Checkout session."""
    url = await service.create_checkout_session(
        x_user_id, data.price_id, data.success_url, data.cancel_url
    )
    return {"url": url}


@router.post("/portal")
async def create_portal(data: PortalRequest, x_customer_id: str = Header()):
    """Create a Stripe Billing Portal session."""
    url = await service.create_portal_session(x_customer_id, data.return_url)
    return {"url": url}


# Webhook route (no auth - Stripe signs it)
webhook_router = APIRouter(tags=["webhooks"])


@webhook_router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Process Stripe webhook events."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    result = await service.handle_webhook(payload, sig)
    return result
