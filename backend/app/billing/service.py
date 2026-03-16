"""Billing service - Stripe integration."""

import asyncio
import logging

import stripe
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.pii import scrub_pii
from app.billing.webhook_handlers import (
    handle_checkout_completed,
    handle_subscription_deleted,
    handle_subscription_updated,
)
from app.core.audit import log_audit_event
from app.core.config import get_settings
from app.core.errors import AuthenticationError, ValidationError

logger = logging.getLogger(__name__)


async def create_checkout_session(
    user_id: str, price_id: str, success_url: str, cancel_url: str
) -> str:
    """Create a Stripe Checkout session and return the URL."""
    session = await asyncio.to_thread(
        stripe.checkout.Session.create,
        mode="subscription",
        customer_email=None,
        metadata={"user_id": user_id},
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.url


async def create_portal_session(customer_id: str, return_url: str) -> str:
    """Create a Stripe Billing Portal session."""
    session = await asyncio.to_thread(
        stripe.billing_portal.Session.create,
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


def _audit_webhook(action: str, resource_id: str, outcome: str = "success") -> None:
    """Log an audit event for a webhook operation."""
    log_audit_event(
        user_id="stripe",
        action=action,
        resource_type="webhook",
        resource_id=resource_id,
        outcome=outcome,
    )


_WEBHOOK_ACTIONS = {
    "checkout.session.completed": "webhook.checkout_completed",
    "customer.subscription.updated": "webhook.subscription_updated",
    "customer.subscription.deleted": "webhook.subscription_deleted",
}

_WEBHOOK_HANDLERS = {
    "checkout.session.completed": handle_checkout_completed,
    "customer.subscription.updated": handle_subscription_updated,
    "customer.subscription.deleted": handle_subscription_deleted,
}


async def handle_webhook(payload: bytes, sig_header: str, db: AsyncSession) -> dict:
    """Process a Stripe webhook event.

    Caller must verify stripe_webhook_secret is set before calling.
    """
    settings = get_settings()

    try:
        event = await asyncio.to_thread(
            stripe.Webhook.construct_event,
            payload,
            sig_header,
            settings.stripe_webhook_secret,
        )
    except stripe.error.SignatureVerificationError:
        _audit_webhook("webhook.signature_failure", "unknown", outcome="failure")
        raise AuthenticationError(message="Invalid webhook signature")
    except ValueError:
        raise ValidationError(message="Invalid webhook payload")

    event_type = event["type"]
    event_data = event.get("data", {}).get("object", {})
    resource_id = event_data.get("id", "unknown")
    action = _WEBHOOK_ACTIONS.get(event_type)

    if action:
        safe_data = scrub_pii(event_data)
        logger.debug("Webhook %s received: %s", event_type, safe_data)
        handler = _WEBHOOK_HANDLERS.get(event_type)
        if handler:
            try:
                await handler(db, event_data)
            except Exception:
                logger.exception(
                    "Webhook handler error for %s: %s", event_type, safe_data
                )
                _audit_webhook(action, resource_id, outcome="failure")
                raise
        _audit_webhook(action, resource_id)
        return {"handled": True, "type": event_type}

    return {"handled": False, "type": event_type}
