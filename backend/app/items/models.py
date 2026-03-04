"""SQLAlchemy models for the items module."""

import enum
import uuid

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class ItemStatus(str, enum.Enum):
    """Status values for an item."""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class Item(Base):
    """Represents a generic item owned by a user.

    This is the starter kit's example domain model.
    Kit buyers should replace this with their own domain model.
    """

    __tablename__ = "items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default=ItemStatus.DRAFT.value)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
