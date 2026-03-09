"""SQLAlchemy models for the users module."""

import uuid

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """Maps a Clerk user to Stripe customer and subscription state.

    This is a local mapping table, not a full user profile.
    """

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    clerk_user_id = Column(String, unique=True, nullable=False, index=True)
    stripe_customer_id = Column(String(255), unique=True, nullable=True, index=True)
    subscription_plan = Column(String(50), nullable=True, default="free")
    subscription_status = Column(String(50), nullable=True, default="none")
    role = Column(String(50), nullable=False, default="member")
    display_name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
