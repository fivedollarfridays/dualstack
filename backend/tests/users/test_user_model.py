"""Tests for the User SQLAlchemy model."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User


class TestUserModel:
    """Test User model instantiation and defaults."""

    @pytest.mark.asyncio
    async def test_create_user_with_defaults(self, db_session: AsyncSession):
        """User created with only clerk_user_id gets correct defaults."""
        user = User(clerk_user_id="clerk_abc123")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.clerk_user_id == "clerk_abc123"
        assert user.stripe_customer_id is None
        assert user.subscription_plan == "free"
        assert user.subscription_status == "none"
        assert user.created_at is not None
        assert user.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_user_with_all_fields(self, db_session: AsyncSession):
        """User created with all fields stores them correctly."""
        user = User(
            clerk_user_id="clerk_xyz",
            stripe_customer_id="cus_stripe123",
            subscription_plan="pro",
            subscription_status="active",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.stripe_customer_id == "cus_stripe123"
        assert user.subscription_plan == "pro"
        assert user.subscription_status == "active"

    @pytest.mark.asyncio
    async def test_clerk_user_id_unique_constraint(self, db_session: AsyncSession):
        """Inserting two users with same clerk_user_id raises IntegrityError."""
        from sqlalchemy.exc import IntegrityError

        user1 = User(clerk_user_id="clerk_dup")
        user2 = User(clerk_user_id="clerk_dup")
        db_session.add(user1)
        await db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_stripe_customer_id_unique_constraint(self, db_session: AsyncSession):
        """Two users cannot share the same stripe_customer_id."""
        from sqlalchemy.exc import IntegrityError

        user1 = User(clerk_user_id="clerk_a", stripe_customer_id="cus_same")
        user2 = User(clerk_user_id="clerk_b", stripe_customer_id="cus_same")
        db_session.add(user1)
        await db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_stripe_customer_id_nullable(self, db_session: AsyncSession):
        """Multiple users can have NULL stripe_customer_id."""
        user1 = User(clerk_user_id="clerk_no_stripe_1")
        user2 = User(clerk_user_id="clerk_no_stripe_2")
        db_session.add_all([user1, user2])
        await db_session.commit()

        result = await db_session.execute(select(User))
        users = result.scalars().all()
        assert len(users) == 2
        assert all(u.stripe_customer_id is None for u in users)

    @pytest.mark.asyncio
    async def test_user_id_auto_generated(self, db_session: AsyncSession):
        """User.id is auto-generated as a UUID string."""
        user = User(clerk_user_id="clerk_autoid")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert isinstance(user.id, str)
        assert len(user.id) == 36  # UUID format
