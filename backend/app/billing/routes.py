"""Billing API routes."""

from fastapi import APIRouter, Depends, HTTPException, Request

from app.billing import service
from app.billing.schemas import CheckoutRequest
from app.core.audit import log_audit_event
from app.core.auth import get_current_user_id
from app.core.config import get_settings
from app.core.errors import ServiceUnavailableError
from app.core.rate_limit import limiter

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout")
@limiter.limit("10/minute")
async def create_checkout(
    request: Request,
    data: CheckoutRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Create a Stripe Checkout session."""
    url = await service.create_checkout_session(
        user_id, data.price_id, data.success_url, data.cancel_url
    )
    log_audit_event(
        user_id=user_id, action="billing.checkout",
        resource_type="checkout", resource_id=data.price_id,
    )
    return {"url": url}


@router.post("/portal")
@limiter.limit("10/minute")
async def create_portal(
    request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """Create a Stripe Billing Portal session.

    Not yet implemented — requires a user->customer mapping table.
    See backend/app/billing/service.py for implementation guidance.
    """
    raise HTTPException(
        status_code=501,
        detail=(
            "Billing portal requires a user->customer mapping. "
            "Store the Stripe customer_id from the checkout.session.completed "
            "webhook in a users table, then look it up here by user_id."
        ),
    )


# Webhook route (no auth - Stripe signs it)
webhook_router = APIRouter(tags=["webhooks"])


@webhook_router.post("/webhooks/stripe")
@limiter.limit("60/minute")
async def stripe_webhook(request: Request):
    """Process Stripe webhook events."""
    settings = get_settings()
    if not settings.stripe_webhook_secret:
        raise ServiceUnavailableError(
            message="Webhook secret not configured",
            error_code="WEBHOOK_NOT_CONFIGURED",
        )
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    result = await service.handle_webhook(payload, sig)
    return result
