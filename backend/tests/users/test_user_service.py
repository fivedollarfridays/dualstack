"""Tests for the User service layer."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User
from app.users.schemas import UserUpdate
from app.core.errors import NotFoundError
from app.users.service import (
    get_or_create_user,
    get_user_by_clerk_id,
    get_user_by_stripe_id,
    link_stripe_customer,
    update_user,
)


class TestGetOrCreateUser:
    """Test get_or_create_user idempotency."""

    @pytest.mark.asyncio
    async def test_creates_new_user(self, db_session: AsyncSession):
        """Creates a user when none exists for the clerk_user_id."""
        user = await get_or_create_user(db_session, "clerk_new")
        assert user.clerk_user_id == "clerk_new"
        assert user.id is not None
        assert user.subscription_plan == "free"

    @pytest.mark.asyncio
    async def test_returns_existing_user(self, db_session: AsyncSession):
        """Returns the same user on second call (idempotent)."""
        user1 = await get_or_create_user(db_session, "clerk_idem")
        user2 = await get_or_create_user(db_session, "clerk_idem")
        assert user1.id == user2.id

    @pytest.mark.asyncio
    async def test_does_not_duplicate(self, db_session: AsyncSession):
        """Calling twice does not create a second row."""
        from sqlalchemy import func, select

        await get_or_create_user(db_session, "clerk_nodup")
        await get_or_create_user(db_session, "clerk_nodup")

        result = await db_session.execute(
            select(func.count())
            .select_from(User)
            .where(User.clerk_user_id == "clerk_nodup")
        )
        assert result.scalar_one() == 1


class TestGetUserByClerkId:
    """Test lookup by clerk_user_id."""

    @pytest.mark.asyncio
    async def test_returns_user(self, db_session: AsyncSession):
        """Returns the user when found."""
        await get_or_create_user(db_session, "clerk_find")
        user = await get_user_by_clerk_id(db_session, "clerk_find")
        assert user is not None
        assert user.clerk_user_id == "clerk_find"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, db_session: AsyncSession):
        """Returns None when no user exists."""
        user = await get_user_by_clerk_id(db_session, "clerk_missing")
        assert user is None


class TestGetUserByStripeId:
    """Test lookup by stripe_customer_id."""

    @pytest.mark.asyncio
    async def test_returns_user(self, db_session: AsyncSession):
        """Returns the user when found by stripe ID."""
        user = await get_or_create_user(db_session, "clerk_stripe_lookup")
        await link_stripe_customer(db_session, "clerk_stripe_lookup", "cus_find")
        found = await get_user_by_stripe_id(db_session, "cus_find")
        assert found is not None
        assert found.id == user.id

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, db_session: AsyncSession):
        """Returns None when no user has that stripe ID."""
        found = await get_user_by_stripe_id(db_session, "cus_nonexist")
        assert found is None


class TestLinkStripeCustomer:
    """Test linking a Stripe customer ID to a user."""

    @pytest.mark.asyncio
    async def test_links_stripe_id(self, db_session: AsyncSession):
        """Sets stripe_customer_id on existing user."""
        await get_or_create_user(db_session, "clerk_link")
        user = await link_stripe_customer(db_session, "clerk_link", "cus_linked")
        assert user.stripe_customer_id == "cus_linked"

    @pytest.mark.asyncio
    async def test_raises_not_found_for_unknown_user(self, db_session: AsyncSession):
        """Raises NotFoundError when clerk_user_id not found."""
        with pytest.raises(NotFoundError, match="User not found"):
            await link_stripe_customer(db_session, "clerk_ghost", "cus_nope")


class TestUpdateUser:
    """Test partial user updates."""

    @pytest.mark.asyncio
    async def test_updates_subscription_fields(self, db_session: AsyncSession):
        """Partial update changes only specified fields."""
        await get_or_create_user(db_session, "clerk_upd")
        data = UserUpdate(subscription_plan="pro", subscription_status="active")
        user = await update_user(db_session, "clerk_upd", data)
        assert user.subscription_plan == "pro"
        assert user.subscription_status == "active"

    @pytest.mark.asyncio
    async def test_unset_fields_not_changed(self, db_session: AsyncSession):
        """Fields not in the update remain unchanged."""
        await get_or_create_user(db_session, "clerk_partial")
        data = UserUpdate(subscription_plan="enterprise")
        user = await update_user(db_session, "clerk_partial", data)
        assert user.subscription_plan == "enterprise"
        assert user.subscription_status == "none"  # unchanged default

    @pytest.mark.asyncio
    async def test_raises_not_found_for_unknown_user(self, db_session: AsyncSession):
        """Raises NotFoundError when clerk_user_id not found."""
        data = UserUpdate(subscription_plan="pro")
        with pytest.raises(NotFoundError, match="User not found"):
            await update_user(db_session, "clerk_nope", data)
