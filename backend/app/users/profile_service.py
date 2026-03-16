"""Profile service — get, update, and delete user profiles."""

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.files.models import FileRecord
from app.items.models import Item
from app.users.models import User
from app.users.service import get_user_by_clerk_id


async def update_profile(
    db: AsyncSession,
    clerk_user_id: str,
    display_name: str | None = None,
    avatar_url: str | None = None,
) -> User:
    """Update profile fields (display_name, avatar_url)."""
    user = await get_user_by_clerk_id(db, clerk_user_id)
    if user is None:
        raise NotFoundError(message="User not found")

    if display_name is not None:
        user.display_name = display_name
    if avatar_url is not None:
        user.avatar_url = avatar_url

    await db.commit()
    await db.refresh(user)
    return user


async def delete_account(db: AsyncSession, clerk_user_id: str) -> None:
    """Permanently delete a user account and all associated data."""
    user = await get_user_by_clerk_id(db, clerk_user_id)
    if user is None:
        raise NotFoundError(message="User not found")

    await db.execute(delete(FileRecord).where(FileRecord.user_id == user.clerk_user_id))
    await db.execute(delete(Item).where(Item.user_id == user.clerk_user_id))
    await db.delete(user)
    await db.commit()
