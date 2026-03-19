"""File service — metadata CRUD and storage coordination."""

import uuid
from pathlib import PurePosixPath

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.core.storage import StorageService
from app.files.models import FileRecord

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


async def request_upload_url(
    db: AsyncSession,
    storage: StorageService,
    user_id: str,
    filename: str,
    content_type: str,
    size: int,
) -> dict:
    if size > MAX_FILE_SIZE:
        raise ValidationError(
            message=f"File size {size} exceeds maximum of {MAX_FILE_SIZE} bytes"
        )

    file_id = str(uuid.uuid4())
    safe_filename = PurePosixPath(filename).name
    if not safe_filename or safe_filename.strip(".") == "":
        raise ValidationError(message="Invalid filename")
    storage_key = f"uploads/{user_id}/{file_id}/{safe_filename}"

    upload_url = storage.generate_upload_url(storage_key, content_type)

    record = FileRecord(
        id=file_id,
        user_id=user_id,
        storage_key=storage_key,
        filename=safe_filename,
        size=size,
        content_type=content_type,
    )
    db.add(record)
    await db.commit()

    return {"file_id": file_id, "upload_url": upload_url}


async def list_files(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 20
) -> tuple[list[FileRecord], int]:
    count_q = (
        select(func.count())
        .select_from(FileRecord)
        .where(FileRecord.user_id == user_id)
    )
    total = (await db.execute(count_q)).scalar_one()

    list_q = (
        select(FileRecord)
        .where(FileRecord.user_id == user_id)
        .order_by(FileRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    files = (await db.execute(list_q)).scalars().all()

    return files, total


async def _get_file_record(
    db: AsyncSession, file_id: str, user_id: str
) -> FileRecord:
    """Fetch a file record scoped to the user, or raise NotFoundError."""
    q = select(FileRecord).where(
        FileRecord.id == file_id, FileRecord.user_id == user_id
    )
    record = (await db.execute(q)).scalar_one_or_none()
    if record is None:
        raise NotFoundError(message="File not found")
    return record


async def get_download_url(
    db: AsyncSession, storage: StorageService, file_id: str, user_id: str
) -> str:
    record = await _get_file_record(db, file_id, user_id)
    return storage.generate_download_url(record.storage_key)


async def delete_file(
    db: AsyncSession, storage: StorageService, file_id: str, user_id: str
) -> None:
    record = await _get_file_record(db, file_id, user_id)
    storage.delete_object(record.storage_key)
    await db.delete(record)
    await db.commit()
