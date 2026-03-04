"""Service layer for items CRUD operations."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.items.models import Item
from app.items.schemas import ItemCreate, ItemUpdate

UPDATABLE_FIELDS: frozenset[str] = frozenset({"title", "description", "status"})


async def create_item(db: AsyncSession, user_id: str, data: ItemCreate) -> Item:
    """Create a new item for the given user.

    Args:
        db: Async database session.
        user_id: ID of the owning user.
        data: Validated item creation data.

    Returns:
        The newly created Item.
    """
    item = Item(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=data.title,
        description=data.description,
        status=data.status,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def list_items(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 20
) -> tuple[list[Item], int]:
    """List items for a user with pagination.

    Args:
        db: Async database session.
        user_id: ID of the owning user.
        skip: Number of items to skip.
        limit: Maximum number of items to return.

    Returns:
        Tuple of (items list, total count).
    """
    count_stmt = select(func.count()).select_from(Item).where(Item.user_id == user_id)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    stmt = select(Item).where(Item.user_id == user_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def get_item(db: AsyncSession, item_id: str, user_id: str) -> Item:
    """Get a single item by ID, scoped to the user.

    Args:
        db: Async database session.
        item_id: ID of the item.
        user_id: ID of the owning user.

    Returns:
        The found Item.

    Raises:
        NotFoundError: If item not found or belongs to a different user.
    """
    stmt = select(Item).where(Item.id == item_id, Item.user_id == user_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if item is None:
        raise NotFoundError(message=f"Item {item_id} not found")
    return item


async def update_item(
    db: AsyncSession, item_id: str, user_id: str, data: ItemUpdate
) -> Item:
    """Update an existing item with partial data.

    Args:
        db: Async database session.
        item_id: ID of the item to update.
        user_id: ID of the owning user.
        data: Validated update data (only set fields are applied).

    Returns:
        The updated Item.

    Raises:
        NotFoundError: If item not found or belongs to a different user.
    """
    item = await get_item(db, item_id=item_id, user_id=user_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in UPDATABLE_FIELDS:
            setattr(item, field, value)

    await db.commit()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, item_id: str, user_id: str) -> None:
    """Delete an item by ID, scoped to the user.

    Args:
        db: Async database session.
        item_id: ID of the item to delete.
        user_id: ID of the owning user.

    Raises:
        NotFoundError: If item not found or belongs to a different user.
    """
    item = await get_item(db, item_id=item_id, user_id=user_id)
    await db.delete(item)
    await db.commit()
