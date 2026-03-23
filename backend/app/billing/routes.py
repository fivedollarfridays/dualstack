"""Billing API routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing import service
from app.billing.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    PortalRequest,
    PortalResponse,
    WebhookResponse,
)
from app.core.audit import persist_audit_event
from app.core.auth import get_current_user_id
from app.core.config import get_settings
from app.core.database import get_db
from app.core.errors import NotFoundError, ServiceUnavailableError
from app.core.rate_limit import limiter
from app.users.service import get_user_by_clerk_id

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout", response_model=CheckoutResponse)
@limiter.limit("10/minute")
async def create_checkout(
    request: Request,
    data: CheckoutRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> CheckoutResponse:
    """Create a Stripe Checkout session."""
    url = await service.create_checkout_session(
        user_id, data.price_id, data.success_url, data.cancel_url
    )
    await persist_audit_event(
        db,
        user_id=user_id,
        action="billing.checkout",
        resource_type="checkout",
        resource_id=data.price_id,
    )
    return {"url": url}


@router.post("/portal", response_model=PortalResponse)
@limiter.limit("10/minute")
async def create_portal(
    request: Request,
    data: PortalRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> PortalResponse:
    """Create a Stripe Billing Portal session."""
    user = await get_user_by_clerk_id(db, user_id)
    if user is None or not user.stripe_customer_id:
        raise NotFoundError(
            message="No billing account found. Please subscribe first.",
        )
    url = await service.create_portal_session(user.stripe_customer_id, data.return_url)
    await persist_audit_event(
        db,
        user_id=user_id,
        action="billing.portal_created",
        resource_type="portal",
        resource_id=user.stripe_customer_id,
    )
    return {"url": url}


# Webhook route (no auth - Stripe signs it)
webhook_router = APIRouter(tags=["webhooks"])


@webhook_router.post("/webhooks/stripe", response_model=WebhookResponse)
@limiter.limit("60/minute")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)) -> WebhookResponse:
    """Process Stripe webhook events."""
    settings = get_settings()
    if not settings.stripe_webhook_secret:
        raise ServiceUnavailableError(
            message="Webhook secret not configured",
            error_code="WEBHOOK_NOT_CONFIGURED",
        )
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    result = await service.handle_webhook(payload, sig, db=db)
    return result
