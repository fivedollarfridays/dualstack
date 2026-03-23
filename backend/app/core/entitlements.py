"""Feature gating — check subscription entitlements."""

from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.plans import (
    ACTIVE_STATUSES,
    DEFAULT_PLAN,
    get_plan_features,
    PLAN_TIERS,
)
from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.core.errors import AuthorizationError
from app.users.service import get_user_by_clerk_id, resolve_plan_status


def _effective_plan(plan: str, status: str) -> str:
    """Return the plan whose features apply, given subscription status."""
    return plan if status in ACTIVE_STATUSES else DEFAULT_PLAN


async def check_feature_access(
    db: AsyncSession, clerk_user_id: str, feature: str
) -> bool:
    """Check if a user's plan grants access to a feature.

    Canceled/inactive users fall back to free-tier features.
    Unknown users default to free plan.
    """
    user = await get_user_by_clerk_id(db, clerk_user_id)
    plan, status = resolve_plan_status(user)
    effective = _effective_plan(plan, status)

    features = get_plan_features(effective)
    return "*" in features or feature in features


def require_feature(feature: str) -> Callable[..., Coroutine[Any, Any, None]]:
    """FastAPI dependency factory that gates access to a feature.

    Usage:
        @router.get("/data", dependencies=[Depends(require_feature("export.csv"))])
        async def get_data(...): ...
    """

    async def _check(
        user_id: str = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
    ):
        allowed = await check_feature_access(db, user_id, feature)
        if not allowed:
            raise AuthorizationError(
                message="This feature requires an upgraded plan.",
            )

    return _check


async def get_user_entitlements(db: AsyncSession, clerk_user_id: str) -> dict:
    """Return entitlements info for a user (plan, status, features, limits)."""
    user = await get_user_by_clerk_id(db, clerk_user_id)
    plan, status = resolve_plan_status(user)
    effective = _effective_plan(plan, status)

    features = get_plan_features(effective)
    limits = PLAN_TIERS.get(effective, PLAN_TIERS[DEFAULT_PLAN])["limits"]

    return {
        "plan": plan,
        "status": status,
        "features": features,
        "limits": dict(limits),
    }
