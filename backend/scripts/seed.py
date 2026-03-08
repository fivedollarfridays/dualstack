"""Database seed script — creates sample data for development.

Usage:
    cd backend && python -m scripts.seed

Idempotent: safe to run multiple times without creating duplicates.
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.items.models import Item, ItemStatus

SEED_USER_ID = "seed-user-001"

SAMPLE_ITEMS = [
    {
        "title": "Welcome to DualStack",
        "description": "Your first item. Edit or delete this to get started.",
        "status": ItemStatus.ACTIVE.value,
    },
    {
        "title": "Set up authentication",
        "description": "Configure Clerk keys in .env to enable real auth.",
        "status": ItemStatus.DRAFT.value,
    },
    {
        "title": "Connect your database",
        "description": "Set DATABASE_URL for production or use local SQLite for dev.",
        "status": ItemStatus.DRAFT.value,
    },
    {
        "title": "Deploy to production",
        "description": "Push to your hosting provider and set environment variables.",
        "status": ItemStatus.DRAFT.value,
    },
    {
        "title": "Customize the domain model",
        "description": "Replace the Item model with your own business entities.",
        "status": ItemStatus.DRAFT.value,
    },
    {
        "title": "Configure Stripe billing",
        "description": "Set STRIPE_SECRET_KEY and create products in the Stripe dashboard.",
        "status": ItemStatus.ARCHIVED.value,
    },
    {
        "title": "Add monitoring",
        "description": "Set up Prometheus + Grafana for observability.",
        "status": ItemStatus.ACTIVE.value,
    },
]


async def seed_items(session: AsyncSession) -> int:
    """Seed sample items into the database.

    Returns the number of items created (0 if all already exist).
    """
    result = await session.execute(
        select(Item.title).where(Item.user_id == SEED_USER_ID)
    )
    existing_titles = set(result.scalars().all())

    created = 0
    for item_data in SAMPLE_ITEMS:
        if item_data["title"] in existing_titles:
            print(f"  Skipped: {item_data['title']} (already exists)")
            continue
        item = Item(user_id=SEED_USER_ID, **item_data)
        session.add(item)
        print(f"  Created: {item_data['title']}")
        created += 1

    await session.commit()
    return created


async def main():
    """Run all seed functions."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.core.database import Base, get_database_url

    url = get_database_url()
    engine = create_async_engine(url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        print("Seeding items...")
        created = await seed_items(session)
        print(f"Done: {created} item(s) created.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
