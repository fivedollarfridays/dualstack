"""Tests for the database seed script."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.items.models import Item, ItemStatus
from app.users.models import User


class TestSeedUser:
    """Test seed_user function — creates demo user."""

    @pytest.mark.asyncio
    async def test_creates_demo_user(self, db_session: AsyncSession):
        """seed_user should create a user with clerk_user_id='dev-user-001'."""
        from scripts.seed import seed_user

        created = await seed_user(db_session)
        assert created is True

        result = await db_session.execute(
            select(User).where(User.clerk_user_id == "dev-user-001")
        )
        user = result.scalar_one()
        assert user.role == "member"

    @pytest.mark.asyncio
    async def test_seed_user_idempotent(self, db_session: AsyncSession):
        """Running seed_user twice should not create duplicates."""
        from scripts.seed import seed_user

        first = await seed_user(db_session)
        second = await seed_user(db_session)
        assert first is True
        assert second is False

        result = await db_session.execute(
            select(User).where(User.clerk_user_id == "dev-user-001")
        )
        users = result.scalars().all()
        assert len(users) == 1


class TestSeedItems:
    """Test seed_items function."""

    @pytest.mark.asyncio
    async def test_creates_exactly_five_items(self, db_session: AsyncSession):
        """seed_items should create exactly 5 sample items."""
        from scripts.seed import SEED_USER_ID, seed_items

        created = await seed_items(db_session)
        assert created == 5

        result = await db_session.execute(
            select(Item).where(Item.user_id == SEED_USER_ID)
        )
        items = result.scalars().all()
        assert len(items) == 5

    @pytest.mark.asyncio
    async def test_status_distribution(self, db_session: AsyncSession):
        """Items should have 2 active, 2 draft, 1 archived."""
        from scripts.seed import SEED_USER_ID, seed_items

        await seed_items(db_session)

        result = await db_session.execute(
            select(Item).where(Item.user_id == SEED_USER_ID)
        )
        items = result.scalars().all()
        statuses = [item.status for item in items]

        assert statuses.count(ItemStatus.ACTIVE.value) == 2
        assert statuses.count(ItemStatus.DRAFT.value) == 2
        assert statuses.count(ItemStatus.ARCHIVED.value) == 1

    @pytest.mark.asyncio
    async def test_items_have_spaced_timestamps(self, db_session: AsyncSession):
        """Items should have created_at timestamps spread over last 7 days."""
        from scripts.seed import SEED_USER_ID, seed_items

        await seed_items(db_session)

        result = await db_session.execute(
            select(Item).where(Item.user_id == SEED_USER_ID)
        )
        items = result.scalars().all()
        timestamps = [item.created_at for item in items if item.created_at]

        assert len(timestamps) == 5
        # All timestamps should be within the last 8 days
        now = datetime.now(timezone.utc)
        for ts in timestamps:
            # Handle naive datetimes from SQLite
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            age = now - ts
            assert age < timedelta(days=8), f"Timestamp {ts} is too old"

        # Timestamps should not all be the same
        unique_timestamps = set(timestamps)
        assert len(unique_timestamps) >= 3, "Timestamps should be spread out"

    @pytest.mark.asyncio
    async def test_idempotent_no_duplicates(self, db_session: AsyncSession):
        """Running seed_items twice should not create duplicates."""
        from scripts.seed import seed_items

        first_count = await seed_items(db_session)
        second_count = await seed_items(db_session)
        assert second_count == 0

        result = await db_session.execute(select(Item))
        items = result.scalars().all()
        assert len(items) == first_count

    @pytest.mark.asyncio
    async def test_items_have_realistic_titles(self, db_session: AsyncSession):
        """Every seeded item should have a non-empty title and description."""
        from scripts.seed import SEED_USER_ID, seed_items

        await seed_items(db_session)

        result = await db_session.execute(
            select(Item).where(Item.user_id == SEED_USER_ID)
        )
        items = result.scalars().all()

        for item in items:
            assert item.user_id == SEED_USER_ID
            assert item.title and len(item.title) > 5
            assert item.description and len(item.description) > 10


class TestSeedConstants:
    """Test seed data constants match requirements."""

    def test_seed_user_id(self):
        from scripts.seed import SEED_USER_ID

        assert SEED_USER_ID == "dev-user-001"

    def test_sample_items_count(self):
        from scripts.seed import SAMPLE_ITEMS

        assert len(SAMPLE_ITEMS) == 5
