"""API routes for file upload and management."""

from fastapi import APIRouter, Depends, Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_audit_event, persist_audit_event
from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.storage import StorageService, get_storage_service
from app.files.schemas import (
    DownloadUrlResponse,
    FileListResponse,
    FileResponse,
    UploadUrlRequest,
    UploadUrlResponse,
)
from app.files.service import (
    delete_file,
    get_download_url,
    list_files,
    request_upload_url,
)

router = APIRouter(prefix="/files", tags=["files"])


def _get_storage() -> StorageService:
    return get_storage_service()


@router.post("/upload-url", response_model=UploadUrlResponse, status_code=201)
@limiter.limit("30/minute")
async def request_upload_url_route(
    request: Request,
    data: UploadUrlRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(_get_storage),
) -> UploadUrlResponse:
    """Generate a presigned upload URL for direct-to-storage upload."""
    result = await request_upload_url(
        db=db,
        storage=storage,
        user_id=user_id,
        filename=data.filename,
        content_type=data.content_type,
        size=data.size,
    )
    await persist_audit_event(
        db,
        user_id=user_id,
        action="upload_request",
        resource_type="file",
        resource_id=result["file_id"],
    )
    return UploadUrlResponse(**result)


@router.get("", response_model=FileListResponse)
@limiter.limit("60/minute")
async def list_files_route(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> FileListResponse:
    """List the authenticated user's uploaded files."""
    skip = (page - 1) * limit
    files, total = await list_files(db, user_id=user_id, skip=skip, limit=limit)
    log_audit_event(
        user_id=user_id, action="list", resource_type="file", resource_id=""
    )
    return FileListResponse(
        files=[FileResponse.model_validate(f) for f in files],
        total=total,
    )


@router.get("/{file_id}/download-url", response_model=DownloadUrlResponse)
@limiter.limit("60/minute")
async def get_download_url_route(
    request: Request,
    file_id: str = Path(..., pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(_get_storage),
) -> DownloadUrlResponse:
    """Generate a presigned download URL for a file."""
    url = await get_download_url(db, storage, file_id=file_id, user_id=user_id)
    await persist_audit_event(
        db,
        user_id=user_id,
        action="download_request",
        resource_type="file",
        resource_id=file_id,
    )
    return DownloadUrlResponse(download_url=url)


@router.delete("/{file_id}", status_code=204)
@limiter.limit("30/minute")
async def delete_file_route(
    request: Request,
    file_id: str = Path(..., pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(_get_storage),
) -> Response:
    """Delete a file and its storage object."""
    await delete_file(db, storage, file_id=file_id, user_id=user_id)
    await persist_audit_event(
        db,
        user_id=user_id,
        action="delete",
        resource_type="file",
        resource_id=file_id,
    )
    return Response(status_code=204)
