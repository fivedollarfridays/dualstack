"""Tests for the database seed script."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.items.models import Item


class TestSeedItems:
    """Test seed_items function."""

    @pytest.mark.asyncio
    async def test_creates_sample_items(self, db_session: AsyncSession):
        """seed_items should create sample items in an empty database."""
        from scripts.seed import seed_items

        created = await seed_items(db_session)
        assert created >= 5

        result = await db_session.execute(select(Item))
        items = result.scalars().all()
        assert len(items) >= 5

    @pytest.mark.asyncio
    async def test_idempotent_no_duplicates(self, db_session: AsyncSession):
        """Running seed_items twice should not create duplicates."""
        from scripts.seed import seed_items

        first_count = await seed_items(db_session)
        second_count = await seed_items(db_session)
        assert second_count == 0  # All already exist

        result = await db_session.execute(select(Item))
        items = result.scalars().all()
        assert len(items) == first_count

    @pytest.mark.asyncio
    async def test_items_have_varied_data(self, db_session: AsyncSession):
        """Seeded items should have different titles and statuses."""
        from scripts.seed import seed_items

        await seed_items(db_session)

        result = await db_session.execute(select(Item))
        items = result.scalars().all()

        titles = {item.title for item in items}
        statuses = {item.status for item in items}
        assert len(titles) >= 5  # All unique titles
        assert len(statuses) >= 2  # At least 2 different statuses

    @pytest.mark.asyncio
    async def test_items_have_required_fields(self, db_session: AsyncSession):
        """Every seeded item should have user_id and title."""
        from scripts.seed import seed_items

        await seed_items(db_session)

        result = await db_session.execute(select(Item))
        items = result.scalars().all()

        for item in items:
            assert item.user_id, f"Item {item.id} missing user_id"
            assert item.title, f"Item {item.id} missing title"
