"""SQLAlchemy models for the admin module."""

import uuid

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    """Persisted audit log entries for the admin audit viewer."""

    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String, nullable=False)
    outcome = Column(String(50), nullable=False, default="success")
    detail = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, server_default=func.now(), index=True)
