"""Role-based access control: roles, permissions, and FastAPI dependencies."""

from enum import Enum
from typing import Callable

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.core.errors import AuthorizationError


class Role(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


# Permission sets per role — admin is a superset of member.
_MEMBER_PERMISSIONS: set[str] = {
    "profile:read",
    "profile:update",
    "items:read",
    "items:create",
    "items:update",
    "items:delete",
}

_ADMIN_PERMISSIONS: set[str] = _MEMBER_PERMISSIONS | {
    "admin:access",
    "users:manage",
    "users:read",
    "settings:manage",
}

ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.ADMIN: _ADMIN_PERMISSIONS,
    Role.MEMBER: _MEMBER_PERMISSIONS,
}


def has_permission(role: Role | str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    if isinstance(role, str):
        role = Role(role)
    return permission in ROLE_PERMISSIONS.get(role, set())


# Role hierarchy — higher value means more privilege.
_ROLE_LEVEL: dict[Role, int] = {
    Role.MEMBER: 1,
    Role.ADMIN: 2,
}


async def _get_user_role(db: AsyncSession, user_id: str) -> Role:
    """Load a user's role from the database, raising if not found."""
    from app.users.models import User

    result = await db.execute(select(User).where(User.clerk_user_id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise AuthorizationError(message="User not found")
    return Role(user.role)


def require_role(required_role: Role) -> Callable:
    """FastAPI dependency factory that enforces a minimum role level.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role(Role.ADMIN))])
    """

    async def _check_role(
        user_id: str = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
    ) -> str:
        user_role = await _get_user_role(db, user_id)
        if _ROLE_LEVEL[user_role] < _ROLE_LEVEL[required_role]:
            raise AuthorizationError(message="Insufficient role")
        return user_id

    return _check_role


def require_permission(permission: str) -> Callable:
    """FastAPI dependency factory that enforces a specific permission.

    Usage:
        @router.get("/users", dependencies=[Depends(require_permission("users:read"))])
    """

    async def _check_permission(
        user_id: str = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
    ) -> str:
        user_role = await _get_user_role(db, user_id)
        if not has_permission(user_role, permission):
            raise AuthorizationError(message="Insufficient permissions")
        return user_id

    return _check_permission
