"""Service layer for user CRUD operations."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.users.models import User
from app.users.schemas import UserUpdate

UPDATABLE_FIELDS: frozenset[str] = frozenset(
    {"stripe_customer_id", "subscription_plan", "subscription_status"}
)


async def get_or_create_user(db: AsyncSession, clerk_user_id: str) -> User:
    """Get existing user or create a new one. Idempotent.

    Handles concurrent creation by catching IntegrityError on the
    unique constraint and retrying the lookup.
    """
    user = await get_user_by_clerk_id(db, clerk_user_id)
    if user is not None:
        return user

    try:
        user = User(clerk_user_id=clerk_user_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        user = await get_user_by_clerk_id(db, clerk_user_id)
        if user is not None:
            return user
        raise


async def get_user_by_clerk_id(db: AsyncSession, clerk_user_id: str) -> User | None:
    """Look up a user by Clerk user ID."""
    result = await db.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    return result.scalar_one_or_none()


async def get_user_by_stripe_id(
    db: AsyncSession, stripe_customer_id: str
) -> User | None:
    """Look up a user by Stripe customer ID."""
    result = await db.execute(
        select(User).where(User.stripe_customer_id == stripe_customer_id)
    )
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, clerk_user_id: str, data: UserUpdate) -> User:
    """Partial update of user fields."""
    user = await get_user_by_clerk_id(db, clerk_user_id)
    if user is None:
        raise NotFoundError(message="User not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in UPDATABLE_FIELDS:
            setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


async def link_stripe_customer(
    db: AsyncSession, clerk_user_id: str, stripe_customer_id: str
) -> User:
    """Link a Stripe customer ID to an existing user."""
    user = await get_user_by_clerk_id(db, clerk_user_id)
    if user is None:
        raise NotFoundError(message="User not found")

    user.stripe_customer_id = stripe_customer_id
    await db.commit()
    await db.refresh(user)
    return user


def resolve_plan_status(user: User | None) -> tuple[str, str]:
    """Extract plan and status from a user, defaulting to free/none.

    This is the single source of truth for default plan/status values.
    """
    if user is None:
        return "free", "none"
    return user.subscription_plan or "free", user.subscription_status or "none"
