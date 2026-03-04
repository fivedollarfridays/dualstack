"""Billing API routes."""

from fastapi import APIRouter, Depends, Request

from app.billing import service
from app.billing.schemas import CheckoutRequest, PortalRequest
from app.core.auth import get_current_user_id

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout")
async def create_checkout(
    data: CheckoutRequest, user_id: str = Depends(get_current_user_id)
):
    """Create a Stripe Checkout session."""
    url = await service.create_checkout_session(
        user_id, data.price_id, data.success_url, data.cancel_url
    )
    return {"url": url}


@router.post("/portal")
async def create_portal(
    data: PortalRequest, user_id: str = Depends(get_current_user_id)
):
    """Create a Stripe Billing Portal session."""
    url = await service.create_portal_session(data.customer_id, data.return_url)
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
