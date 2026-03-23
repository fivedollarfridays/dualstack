"""Service layer for items CRUD operations."""

import uuid

from typing import Literal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import escape_like
from app.core.errors import NotFoundError
from app.items.models import Item
from app.items.schemas import ItemCreate, ItemUpdate

UPDATABLE_FIELDS: frozenset[str] = frozenset({"title", "description", "status"})

SORTABLE_FIELDS = {
    "title": Item.title,
    "created_at": Item.created_at,
    "updated_at": Item.updated_at,
}
SortField = Literal["title", "created_at", "updated_at"]
SortDir = Literal["asc", "desc"]


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
    db: AsyncSession,
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    search: str | None = None,
    sort_by: SortField = "created_at",
    sort_dir: SortDir = "desc",
    status: str | None = None,
) -> tuple[list[Item], int]:
    """List items with search, sort, filter, and pagination."""
    base = select(Item).where(Item.user_id == user_id)
    count_base = select(func.count()).select_from(Item).where(Item.user_id == user_id)

    if search:
        pattern = f"%{escape_like(search)}%"
        search_cond = or_(Item.title.ilike(pattern), Item.description.ilike(pattern))
        base = base.where(search_cond)
        count_base = count_base.where(search_cond)

    if status:
        base = base.where(Item.status == status)
        count_base = count_base.where(Item.status == status)

    total = (await db.execute(count_base)).scalar_one()

    column = SORTABLE_FIELDS[sort_by]
    order = column.asc() if sort_dir == "asc" else column.desc()
    stmt = base.order_by(order, Item.id.desc()).offset(skip).limit(limit)
    items = list((await db.execute(stmt)).scalars().all())

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
        raise NotFoundError(message="Item not found")
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
