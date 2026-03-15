"""Pydantic schemas for file upload endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class UploadUrlRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., min_length=1, max_length=127)
    size: int = Field(..., gt=0)


class UploadUrlResponse(BaseModel):
    file_id: str
    upload_url: str
    storage_key: str


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
