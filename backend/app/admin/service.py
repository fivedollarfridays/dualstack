"""Admin business logic — user management, health, audit log."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models import AuditLog
from app.core.database import escape_like
from app.core.errors import NotFoundError, ValidationError
from app.core.rbac import Role
from app.users.models import User


async def list_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    search: str | None = None,
) -> tuple[list[User], int]:
    """List users with optional search filter and pagination."""
    base = select(User)
    count_base = select(func.count()).select_from(User)

    if search:
        pattern = f"%{escape_like(search)}%"
        condition = User.clerk_user_id.ilike(pattern)
        base = base.where(condition)
        count_base = count_base.where(condition)

    total = (await db.execute(count_base)).scalar_one()

    stmt = base.order_by(User.created_at.desc()).offset(skip).limit(limit)
    users = list((await db.execute(stmt)).scalars().all())

    return users, total


async def assign_role(db: AsyncSession, user_id: str, role: str) -> User:
    """Assign a role to a user by their internal ID."""
    # Validate role value
    try:
        Role(role)
    except ValueError:
        raise ValidationError(message="Invalid role value")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundError(message="User not found")

    # Prevent last-admin lockout
    if user.role == "admin" and role != "admin":
        admin_count = (
            await db.execute(
                select(func.count()).select_from(User).where(User.role == "admin")
            )
        ).scalar_one()
        if admin_count <= 1:
            raise ValidationError(message="Cannot demote the last admin")

    user.role = role
    await db.commit()
    await db.refresh(user)
    return user


async def get_health(db: AsyncSession) -> dict:
    """Return system health metrics."""
    try:
        total = (await db.execute(select(func.count()).select_from(User))).scalar_one()
        return {
            "status": "healthy",
            "database": "connected",
            "user_count": total,
        }
    except Exception:
        return {
            "status": "unhealthy",
            "database": "error",
            "user_count": 0,
        }


async def list_audit_logs(
    db: AsyncSession, skip: int = 0, limit: int = 50
) -> tuple[list[AuditLog], int]:
    """List audit log entries with pagination."""
    total = (await db.execute(select(func.count()).select_from(AuditLog))).scalar_one()

    stmt = (
        select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    )
    entries = list((await db.execute(stmt)).scalars().all())
    return entries, total
