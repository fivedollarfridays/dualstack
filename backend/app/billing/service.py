"""Billing service - Stripe integration."""

import stripe

from app.core.config import get_settings


def get_stripe():
    """Configure and return the stripe module."""
    settings = get_settings()
    stripe.api_key = settings.stripe_secret_key
    return stripe


async def create_checkout_session(
    user_id: str, price_id: str, success_url: str, cancel_url: str
) -> str:
    """Create a Stripe Checkout session and return the URL."""
    s = get_stripe()
    session = s.checkout.Session.create(
        mode="subscription",
        customer_email=None,
        metadata={"user_id": user_id},
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.url


async def create_portal_session(customer_id: str, return_url: str) -> str:
    """Create a Stripe Billing Portal session and return the URL."""
    s = get_stripe()
    session = s.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


async def handle_webhook(payload: bytes, sig_header: str) -> dict:
    """Process a Stripe webhook event."""
    settings = get_settings()
    s = get_stripe()
    event = s.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)

    if event["type"] == "checkout.session.completed":
        return {"handled": True, "type": event["type"]}
    elif event["type"] == "customer.subscription.updated":
        return {"handled": True, "type": event["type"]}

    return {"handled": False, "type": event["type"]}
