"""API routes for user subscription info and profile management."""

from fastapi import APIRouter, Depends, Header, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import persist_audit_event
from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.core.errors import NotFoundError, ValidationError
from app.core.rate_limit import limiter
from app.users.profile_service import delete_account, update_profile
from app.users.schemas import (
    SubscriptionInfoResponse,
    UserProfileResponse,
    UserProfileUpdate,
)
from app.users.service import get_user_by_clerk_id, resolve_plan_status

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=SubscriptionInfoResponse)
@limiter.limit("60/minute")
async def get_current_user(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionInfoResponse:
    """Return the authenticated user's subscription info."""
    user = await get_user_by_clerk_id(db, user_id)
    plan, status = resolve_plan_status(user)
    return SubscriptionInfoResponse(subscription_plan=plan, subscription_status=status)


@router.get("/me/profile", response_model=UserProfileResponse)
@limiter.limit("60/minute")
async def get_user_profile(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Return the authenticated user's full profile."""
    user = await get_user_by_clerk_id(db, user_id)
    if user is None:
        raise NotFoundError(message="User not found")
    return UserProfileResponse.model_validate(user)


@router.patch("/me/profile", response_model=UserProfileResponse)
@limiter.limit("30/minute")
async def update_user_profile(
    request: Request,
    body: UserProfileUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Update the authenticated user's profile."""
    data = body.model_dump(exclude_unset=True)
    user = await update_profile(db, user_id, **data)
    await persist_audit_event(
        db,
        user_id=user_id,
        action="profile.update",
        resource_type="user",
        resource_id=user_id,
    )
    return UserProfileResponse.model_validate(user)


CONFIRM_PHRASE = "DELETE MY ACCOUNT"


@router.delete("/me", status_code=204)
@limiter.limit("3/minute")
async def delete_user_account(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    x_confirm_delete: str | None = Header(None),
) -> Response:
    """Delete the authenticated user's account. Requires confirmation header."""
    if not x_confirm_delete or x_confirm_delete != CONFIRM_PHRASE:
        raise ValidationError(
            message="Account deletion requires confirmation via the X-Confirm-Delete header."
        )
    # Persist audit event BEFORE deletion — delete_account commits the session,
    # so a post-delete flush would never be committed.
    await persist_audit_event(
        db,
        user_id=user_id,
        action="account.delete",
        resource_type="user",
        resource_id=user_id,
    )
    await delete_account(db, user_id)
    return Response(status_code=204)
