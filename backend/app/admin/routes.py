"""Admin API endpoints — protected with require_role(Role.ADMIN)."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.schemas import (
    AuditLogEntry,
    AuditLogResponse,
    HealthResponse,
    RoleUpdateRequest,
    UserAdminResponse,
    UserListResponse,
)
from app.admin.service import assign_role, get_health, list_audit_logs, list_users
from app.core.audit import persist_audit_event
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.rbac import Role, require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=UserListResponse)
@limiter.limit("60/minute")
async def admin_list_users(
    request: Request,
    _admin_id: str = Depends(require_role(Role.ADMIN)),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> UserListResponse:
    skip = (page - 1) * limit
    users, total = await list_users(db, skip=skip, limit=limit, search=search)
    return UserListResponse(
        users=[UserAdminResponse.model_validate(u) for u in users],
        total=total,
    )


@router.patch("/users/{user_id}/role", response_model=UserAdminResponse)
@limiter.limit("10/minute")
async def admin_update_role(
    request: Request,
    user_id: str,
    body: RoleUpdateRequest,
    admin_id: str = Depends(require_role(Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> UserAdminResponse:
    user = await assign_role(db, user_id=user_id, role=body.role)
    await persist_audit_event(
        db,
        user_id=admin_id,
        action="role.assign",
        resource_type="user",
        resource_id=user_id,
        detail=f"role={body.role}",
    )
    return UserAdminResponse.model_validate(user)


@router.get("/health", response_model=HealthResponse)
@limiter.limit("60/minute")
async def admin_health(
    request: Request,
    _admin_id: str = Depends(require_role(Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> HealthResponse:
    health = await get_health(db)
    return HealthResponse(**health)


@router.get("/audit", response_model=AuditLogResponse)
@limiter.limit("60/minute")
async def admin_audit_log(
    request: Request,
    _admin_id: str = Depends(require_role(Role.ADMIN)),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> AuditLogResponse:
    skip = (page - 1) * limit
    entries, total = await list_audit_logs(db, skip=skip, limit=limit)
    return AuditLogResponse(
        entries=[AuditLogEntry.model_validate(e) for e in entries],
        total=total,
    )
