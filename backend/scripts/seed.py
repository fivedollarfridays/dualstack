"""Database seed script — creates sample data for development.

Usage:
    cd backend && python -m scripts.seed

Idempotent: safe to run multiple times without creating duplicates.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.items.models import Item, ItemStatus
from app.users.models import User

SEED_USER_ID = "dev-user-001"

SAMPLE_ITEMS = [
    {
        "title": "Welcome to DualStack",
        "description": "Your first item. Edit or delete this to get started.",
        "status": ItemStatus.ACTIVE.value,
        "days_ago": 6,
    },
    {
        "title": "Set up authentication",
        "description": "Configure Clerk keys in .env to enable real auth.",
        "status": ItemStatus.ACTIVE.value,
        "days_ago": 5,
    },
    {
        "title": "Connect your database",
        "description": "Set DATABASE_URL for production or use local SQLite for dev.",
        "status": ItemStatus.DRAFT.value,
        "days_ago": 3,
    },
    {
        "title": "Deploy to production",
        "description": "Push to your hosting provider and set environment variables.",
        "status": ItemStatus.DRAFT.value,
        "days_ago": 1,
    },
    {
        "title": "Configure Stripe billing",
        "description": "Set STRIPE_SECRET_KEY and create products in the Stripe dashboard.",
        "status": ItemStatus.ARCHIVED.value,
        "days_ago": 0,
    },
]


async def seed_user(session: AsyncSession) -> bool:
    """Seed the demo user into the database.

    Returns True if user was created, False if already exists.
    """
    result = await session.execute(
        select(User).where(User.clerk_user_id == SEED_USER_ID)
    )
    if result.scalar_one_or_none() is not None:
        print(f"  Skipped: user {SEED_USER_ID} (already exists)")
        return False

    user = User(clerk_user_id=SEED_USER_ID, role="member")
    session.add(user)
    await session.commit()
    print(f"  Created: user {SEED_USER_ID}")
    return True


async def seed_items(session: AsyncSession) -> int:
    """Seed sample items into the database.

    Returns the number of items created (0 if all already exist).
    """
    result = await session.execute(
        select(Item.title).where(Item.user_id == SEED_USER_ID)
    )
    existing_titles = set(result.scalars().all())

    now = datetime.now(timezone.utc)
    created = 0
    for item_data in SAMPLE_ITEMS:
        if item_data["title"] in existing_titles:
            print(f"  Skipped: {item_data['title']} (already exists)")
            continue
        days_ago = item_data.get("days_ago", 0)
        created_at = now - timedelta(days=days_ago)
        item = Item(
            user_id=SEED_USER_ID,
            title=item_data["title"],
            description=item_data["description"],
            status=item_data["status"],
            created_at=created_at,
        )
        session.add(item)
        print(f"  Created: {item_data['title']}")
        created += 1

    await session.commit()
    return created


async def main():
    """Run all seed functions."""
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    from app.core.database import Base, get_database_url

    url = get_database_url()
    engine = create_async_engine(url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with factory() as session:
        print("Seeding user...")
        await seed_user(session)
        print("Seeding items...")
        created = await seed_items(session)
        print(f"Done: {created} item(s) created.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
