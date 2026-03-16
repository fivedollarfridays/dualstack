"""Tests for billing webhook handler functions."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User
from app.users.service import get_or_create_user, link_stripe_customer


class TestHandleCheckoutCompleted:
    """Test checkout.session.completed handler."""

    @pytest.mark.asyncio
    async def test_creates_user_and_links_stripe(self, db_session: AsyncSession):
        """Links Stripe customer to Clerk user on checkout completion."""
        from app.billing.webhook_handlers import handle_checkout_completed

        event_data = {
            "customer": "cus_new_123",
            "subscription": "sub_new_456",
            "metadata": {"user_id": "clerk_checkout_user"},
            "line_items": {
                "data": [{"price": {"id": "price_pro", "lookup_key": "pro"}}]
            },
        }
        await handle_checkout_completed(db_session, event_data)

        user = await db_session.execute(
            select(User).where(User.clerk_user_id == "clerk_checkout_user")
        )
        user = user.scalar_one()
        assert user.stripe_customer_id == "cus_new_123"
        assert user.subscription_status == "active"
        assert user.subscription_plan == "pro"

    @pytest.mark.asyncio
    async def test_idempotent_replay(self, db_session: AsyncSession):
        """Replaying the same event does not create duplicates or error."""
        from app.billing.webhook_handlers import handle_checkout_completed

        event_data = {
            "customer": "cus_idem_123",
            "subscription": "sub_idem_456",
            "metadata": {"user_id": "clerk_idem_user"},
            "line_items": {
                "data": [{"price": {"id": "price_pro", "lookup_key": "pro"}}]
            },
        }
        await handle_checkout_completed(db_session, event_data)
        await handle_checkout_completed(db_session, event_data)

        result = await db_session.execute(
            select(User).where(User.clerk_user_id == "clerk_idem_user")
        )
        users = result.scalars().all()
        assert len(users) == 1
        assert users[0].stripe_customer_id == "cus_idem_123"

    @pytest.mark.asyncio
    async def test_missing_user_id_logs_warning(self, db_session: AsyncSession):
        """Missing metadata.user_id logs warning but does not crash."""
        from app.billing.webhook_handlers import handle_checkout_completed

        event_data = {
            "customer": "cus_no_uid",
            "subscription": "sub_no_uid",
            "metadata": {},
        }
        # Should not raise
        await handle_checkout_completed(db_session, event_data)

    @pytest.mark.asyncio
    async def test_missing_metadata_logs_warning(self, db_session: AsyncSession):
        """Missing metadata entirely logs warning but does not crash."""
        from app.billing.webhook_handlers import handle_checkout_completed

        event_data = {
            "customer": "cus_no_meta",
            "subscription": "sub_no_meta",
        }
        await handle_checkout_completed(db_session, event_data)

    @pytest.mark.asyncio
    async def test_missing_customer_id_logs_warning(self, db_session: AsyncSession):
        """Missing customer field logs warning and returns without creating user."""
        from app.billing.webhook_handlers import handle_checkout_completed

        event_data = {
            "subscription": "sub_no_cus",
            "metadata": {"user_id": "clerk_no_cus_user"},
        }
        await handle_checkout_completed(db_session, event_data)

        result = await db_session.execute(
            select(User).where(User.clerk_user_id == "clerk_no_cus_user")
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_defaults_plan_to_pro_without_line_items(
        self, db_session: AsyncSession
    ):
        """Checkout without line_items defaults subscription_plan to 'pro'."""
        from app.billing.webhook_handlers import handle_checkout_completed

        event_data = {
            "customer": "cus_no_items",
            "subscription": "sub_no_items",
            "metadata": {"user_id": "clerk_no_items_user"},
        }
        await handle_checkout_completed(db_session, event_data)

        user = await db_session.execute(
            select(User).where(User.clerk_user_id == "clerk_no_items_user")
        )
        user = user.scalar_one()
        assert user.subscription_plan == "pro"


class TestHandleSubscriptionUpdated:
    """Test customer.subscription.updated handler."""

    @pytest.mark.asyncio
    async def test_updates_plan_and_status(self, db_session: AsyncSession):
        """Updates subscription plan and status from event data."""
        from app.billing.webhook_handlers import handle_subscription_updated

        user = await get_or_create_user(db_session, "clerk_sub_upd")
        await link_stripe_customer(db_session, "clerk_sub_upd", "cus_sub_upd")

        event_data = {
            "customer": "cus_sub_upd",
            "status": "active",
            "items": {"data": [{"price": {"id": "price_pro", "lookup_key": "pro"}}]},
        }
        await handle_subscription_updated(db_session, event_data)

        await db_session.refresh(user)
        assert user.subscription_plan == "pro"
        assert user.subscription_status == "active"

    @pytest.mark.asyncio
    async def test_uses_price_id_when_no_lookup_key(self, db_session: AsyncSession):
        """Falls back to price ID when lookup_key is absent."""
        from app.billing.webhook_handlers import handle_subscription_updated

        await get_or_create_user(db_session, "clerk_no_key")
        await link_stripe_customer(db_session, "clerk_no_key", "cus_no_key")

        event_data = {
            "customer": "cus_no_key",
            "status": "active",
            "items": {"data": [{"price": {"id": "price_enterprise_monthly"}}]},
        }
        await handle_subscription_updated(db_session, event_data)

        user = await db_session.execute(
            select(User).where(User.clerk_user_id == "clerk_no_key")
        )
        user = user.scalar_one()
        assert user.subscription_plan == "price_enterprise_monthly"

    @pytest.mark.asyncio
    async def test_unknown_customer_does_not_crash(self, db_session: AsyncSession):
        """Unknown stripe customer logs warning but does not raise."""
        from app.billing.webhook_handlers import handle_subscription_updated

        event_data = {
            "customer": "cus_ghost",
            "status": "active",
            "items": {"data": [{"price": {"id": "price_x"}}]},
        }
        # Should not raise
        await handle_subscription_updated(db_session, event_data)

    @pytest.mark.asyncio
    async def test_idempotent_replay(self, db_session: AsyncSession):
        """Replaying the same event produces the same result."""
        from app.billing.webhook_handlers import handle_subscription_updated

        await get_or_create_user(db_session, "clerk_replay")
        await link_stripe_customer(db_session, "clerk_replay", "cus_replay")

        event_data = {
            "customer": "cus_replay",
            "status": "past_due",
            "items": {"data": [{"price": {"id": "price_pro", "lookup_key": "pro"}}]},
        }
        await handle_subscription_updated(db_session, event_data)
        await handle_subscription_updated(db_session, event_data)

        user = await db_session.execute(
            select(User).where(User.clerk_user_id == "clerk_replay")
        )
        user = user.scalar_one()
        assert user.subscription_status == "past_due"
        assert user.subscription_plan == "pro"


class TestHandleSubscriptionDeleted:
    """Test customer.subscription.deleted handler."""

    @pytest.mark.asyncio
    async def test_marks_canceled_and_free(self, db_session: AsyncSession):
        """Sets subscription_status to canceled and plan to free."""
        from app.billing.webhook_handlers import handle_subscription_deleted

        await get_or_create_user(db_session, "clerk_del")
        await link_stripe_customer(db_session, "clerk_del", "cus_del")

        event_data = {
            "customer": "cus_del",
            "status": "canceled",
        }
        await handle_subscription_deleted(db_session, event_data)

        user = await db_session.execute(
            select(User).where(User.clerk_user_id == "clerk_del")
        )
        user = user.scalar_one()
        assert user.subscription_status == "canceled"
        assert user.subscription_plan == "free"

    @pytest.mark.asyncio
    async def test_unknown_customer_does_not_crash(self, db_session: AsyncSession):
        """Unknown stripe customer logs warning but does not raise."""
        from app.billing.webhook_handlers import handle_subscription_deleted

        event_data = {"customer": "cus_unknown_del", "status": "canceled"}
        await handle_subscription_deleted(db_session, event_data)

    @pytest.mark.asyncio
    async def test_idempotent_replay(self, db_session: AsyncSession):
        """Replaying deletion event is safe."""
        from app.billing.webhook_handlers import handle_subscription_deleted

        await get_or_create_user(db_session, "clerk_del_idem")
        await link_stripe_customer(db_session, "clerk_del_idem", "cus_del_idem")

        event_data = {"customer": "cus_del_idem", "status": "canceled"}
        await handle_subscription_deleted(db_session, event_data)
        await handle_subscription_deleted(db_session, event_data)

        user = await db_session.execute(
            select(User).where(User.clerk_user_id == "clerk_del_idem")
        )
        user = user.scalar_one()
        assert user.subscription_status == "canceled"
        assert user.subscription_plan == "free"
