"""Pydantic schemas for the items module."""

from datetime import datetime

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Schema for creating a new item."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: str = "draft"


class ItemUpdate(BaseModel):
    """Schema for updating an existing item. All fields optional."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = None


class ItemResponse(BaseModel):
    """Schema for returning an item in API responses."""

    model_config = {"from_attributes": True}

    id: str
    user_id: str
    title: str
    description: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class ItemListResponse(BaseModel):
    """Schema for returning a paginated list of items."""

    items: list[ItemResponse]
    total: int
