"""Pydantic schemas for file upload endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

ALLOWED_CONTENT_TYPES = frozenset(
    {
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/webp",
        "application/pdf",
        "text/plain",
        "text/csv",
        "application/json",
    }
)


class UploadUrlRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., min_length=1, max_length=127)
    size: int = Field(..., gt=0, le=104857600)

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        if v not in ALLOWED_CONTENT_TYPES:
            raise ValueError("Content type is not allowed")
        return v


class UploadUrlResponse(BaseModel):
    file_id: str
    upload_url: str


class FileResponse(BaseModel):
    id: str
    filename: str
    size: int
    content_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FileListResponse(BaseModel):
    files: list[FileResponse]
    total: int


class DownloadUrlResponse(BaseModel):
    download_url: str
