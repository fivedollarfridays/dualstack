"""Billing service - Stripe integration."""

import asyncio

import stripe

from app.core.config import get_settings


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


async def handle_webhook(payload: bytes, sig_header: str) -> dict:
    """Process a Stripe webhook event."""
    settings = get_settings()
    event = await asyncio.to_thread(
        stripe.Webhook.construct_event,
        payload,
        sig_header,
        settings.stripe_webhook_secret,
    )

    if event["type"] == "checkout.session.completed":
        return {"handled": True, "type": event["type"]}
    elif event["type"] == "customer.subscription.updated":
        return {"handled": True, "type": event["type"]}

    return {"handled": False, "type": event["type"]}
