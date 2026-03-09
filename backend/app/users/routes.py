"""API routes for user subscription info."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.users.schemas import SubscriptionInfoResponse
from app.users.service import get_user_by_clerk_id, resolve_plan_status

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=SubscriptionInfoResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Return the authenticated user's subscription info."""
    user = await get_user_by_clerk_id(db, user_id)
    plan, status = resolve_plan_status(user)
    return SubscriptionInfoResponse(subscription_plan=plan, subscription_status=status)
