"""Pydantic schemas for the users module."""

from datetime import datetime

from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


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


class UserProfileResponse(BaseModel):
    """Profile data returned by /users/me/profile."""

    model_config = {"from_attributes": True}

    clerk_user_id: str
    display_name: str | None = None
    avatar_url: str | None = None
    role: str = "member"
    subscription_plan: str | None = "free"
    subscription_status: str | None = "none"
    created_at: datetime


class UserProfileUpdate(BaseModel):
    """Partial update for profile fields."""

    display_name: str | None = Field(None, min_length=1, max_length=255)
    avatar_url: str | None = Field(None, min_length=1, max_length=2000)

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v: str | None) -> str | None:
        """Only allow HTTPS avatar URLs to prevent XSS via javascript:/data: schemes."""
        if not v:
            return v
        parsed = urlparse(v)
        if parsed.scheme != "https":
            raise ValueError("Avatar URL must use HTTPS")
        if not parsed.netloc:
            raise ValueError("Avatar URL must have a valid host")
        return v


