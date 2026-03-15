"""SQLAlchemy models for the files module."""

import uuid

from sqlalchemy import BigInteger, Column, DateTime, String
from sqlalchemy.sql import func

from app.core.database import Base


class FileRecord(Base):
    """Tracks metadata for files uploaded to S3/R2 storage."""

    __tablename__ = "file_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    storage_key = Column(String, nullable=False, unique=True)
    filename = Column(String(255), nullable=False)
    size = Column(BigInteger, nullable=False)
    content_type = Column(String(127), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
