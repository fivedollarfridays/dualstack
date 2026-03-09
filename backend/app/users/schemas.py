"""Pydantic schemas for the users module."""

from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Schema for creating a new user. Only clerk_user_id is required."""

    clerk_user_id: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    """Schema for partial user updates (subscription fields)."""

    stripe_customer_id: str | None = None
    subscription_plan: str | None = None
    subscription_status: str | None = None


class SubscriptionInfoResponse(BaseModel):
    """Public-facing subscription info (no internal fields)."""

    subscription_plan: str = "free"
    subscription_status: str = "none"


class UserResponse(BaseModel):
    """Schema for returning a user in API responses."""

    model_config = {"from_attributes": True}

    id: str
    clerk_user_id: str
    stripe_customer_id: str | None = None
    subscription_plan: str | None = "free"
    subscription_status: str | None = "none"
    created_at: datetime
    updated_at: datetime
