"""Billing service - Stripe integration."""

import asyncio

import stripe

from app.core.audit import log_audit_event
from app.core.config import get_settings
from app.core.errors import AuthenticationError, ValidationError


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
    """Create a Stripe Billing Portal session.

    NOTE: To use this in production, you need a user->customer mapping.
    Store the Stripe customer ID from the checkout.session.completed webhook
    in your database, then look it up here instead of accepting it as input.
    """
    session = await asyncio.to_thread(
        stripe.billing_portal.Session.create,
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


def _audit_webhook(action: str, resource_id: str, outcome: str = "success") -> None:
    """Log an audit event for a webhook operation."""
    log_audit_event(
        user_id="stripe", action=action,
        resource_type="webhook", resource_id=resource_id, outcome=outcome,
    )


_WEBHOOK_ACTIONS = {
    "checkout.session.completed": "webhook.checkout_completed",
    "customer.subscription.updated": "webhook.subscription_updated",
}


async def handle_webhook(payload: bytes, sig_header: str) -> dict:
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
    resource_id = event.get("data", {}).get("object", {}).get("id", "unknown")
    action = _WEBHOOK_ACTIONS.get(event_type)

    if action:
        _audit_webhook(action, resource_id)
        return {"handled": True, "type": event_type}

    return {"handled": False, "type": event_type}
