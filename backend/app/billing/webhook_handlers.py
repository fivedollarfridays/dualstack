"""Webhook event handlers — persist Stripe subscription state to database."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.users.service import get_or_create_user, get_user_by_stripe_id

logger = logging.getLogger(__name__)

VALID_STRIPE_STATUSES = frozenset({
    "active", "trialing", "past_due", "canceled",
    "unpaid", "incomplete", "incomplete_expired",
})


async def handle_checkout_completed(db: AsyncSession, event_data: dict) -> None:
    """Process checkout.session.completed — link Stripe customer to Clerk user."""
    metadata = event_data.get("metadata") or {}
    user_id = metadata.get("user_id")

    if not user_id:
        logger.warning(
            "checkout.session.completed missing metadata.user_id, skipping: %s",
            event_data.get("id", "unknown"),
        )
        return

    customer_id = event_data.get("customer")
    if not customer_id:
        logger.warning(
            "checkout.session.completed missing customer, skipping: %s",
            event_data.get("id", "unknown"),
        )
        return

    user = await get_or_create_user(db, clerk_user_id=user_id)
    user.stripe_customer_id = customer_id
    user.subscription_status = "active"
    user.subscription_plan = _extract_plan_from_checkout(event_data)
    await db.commit()
    await db.refresh(user)


async def handle_subscription_updated(db: AsyncSession, event_data: dict) -> None:
    """Process customer.subscription.updated — sync plan and status."""
    customer_id = event_data.get("customer")
    user = await get_user_by_stripe_id(db, stripe_customer_id=customer_id)

    if user is None:
        logger.warning(
            "subscription.updated for unknown customer %s, skipping", customer_id
        )
        return

    raw_status = event_data.get("status", "unknown")
    user.subscription_status = raw_status if raw_status in VALID_STRIPE_STATUSES else "unknown"
    user.subscription_plan = _extract_plan(event_data)
    await db.commit()
    await db.refresh(user)


async def handle_subscription_deleted(db: AsyncSession, event_data: dict) -> None:
    """Process customer.subscription.deleted — mark canceled, revert to free."""
    customer_id = event_data.get("customer")
    user = await get_user_by_stripe_id(db, stripe_customer_id=customer_id)

    if user is None:
        logger.warning(
            "subscription.deleted for unknown customer %s, skipping", customer_id
        )
        return

    user.subscription_status = "canceled"
    user.subscription_plan = "free"
    await db.commit()
    await db.refresh(user)


def _extract_plan(event_data: dict) -> str:
    """Extract plan name from subscription event data."""
    items = event_data.get("items", {}).get("data", [])
    if items:
        price = items[0].get("price", {})
        return price.get("lookup_key") or price.get("id", "unknown")
    return "unknown"


def _extract_plan_from_checkout(event_data: dict) -> str:
    """Extract plan name from checkout.session.completed event data.

    Checkout sessions store line items differently from subscriptions.
    Falls back to 'pro' if line item data is unavailable (common when
    line_items are not expanded in the webhook payload).
    """
    line_items = event_data.get("line_items", {}).get("data", [])
    if line_items:
        price = line_items[0].get("price", {})
        return price.get("lookup_key") or price.get("id", "unknown")
    return "pro"
