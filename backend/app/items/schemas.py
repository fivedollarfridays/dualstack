"""Pydantic schemas for the items module."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ItemStatusType = Literal["draft", "active", "archived"]


class ItemCreate(BaseModel):
    """Schema for creating a new item."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=10000)
    status: ItemStatusType = "draft"


class ItemUpdate(BaseModel):
    """Schema for updating an existing item. All fields optional."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=10000)
    status: ItemStatusType | None = None


class ItemResponse(BaseModel):
    """Schema for returning an item in API responses."""

    model_config = {"from_attributes": True}

    id: str
    title: str
    description: str | None = None
    status: ItemStatusType
    created_at: datetime
    updated_at: datetime


class ItemListResponse(BaseModel):
    """Schema for returning a paginated list of items."""

    items: list[ItemResponse]
    total: int
