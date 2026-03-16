"""Pydantic schemas for admin endpoints."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class UserAdminResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    clerk_user_id: str
    role: str
    subscription_plan: str | None = None
    subscription_status: str | None = None
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    users: list[UserAdminResponse]
    total: int


class RoleUpdateRequest(BaseModel):
    role: Literal["admin", "member"]


class HealthResponse(BaseModel):
    status: str
    database: str
    user_count: int


class AuditLogEntry(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    outcome: str
    detail: str
    created_at: datetime


class AuditLogResponse(BaseModel):
    entries: list[AuditLogEntry]
    total: int
