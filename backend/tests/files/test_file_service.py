"""Tests for file service — metadata CRUD and storage coordination."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.errors import NotFoundError, ValidationError


def _make_file_record(
    file_id: str = "file-1",
    user_id: str = "user-1",
    key: str = "uploads/user-1/abc.png",
    filename: str = "photo.png",
    size: int = 1024,
    content_type: str = "image/png",
) -> MagicMock:
    f = MagicMock()
    f.id = file_id
    f.user_id = user_id
    f.storage_key = key
    f.filename = filename
    f.size = size
    f.content_type = content_type
    f.created_at = datetime(2026, 1, 1)
    return f


class TestRequestUploadUrl:
    async def test_returns_presigned_url_and_file_id(self):
        from app.files.service import request_upload_url

        db = AsyncMock()
        storage = MagicMock()
        storage.generate_upload_url.return_value = "https://s3.example.com/signed"

        result = await request_upload_url(
            db=db,
            storage=storage,
            user_id="user-1",
            filename="photo.png",
            content_type="image/png",
            size=2048,
        )

        assert result["upload_url"] == "https://s3.example.com/signed"
        assert "file_id" in result
        assert "storage_key" not in result
        db.add.assert_called_once()
        db.commit.assert_awaited_once()

    async def test_rejects_oversized_file(self):
        from app.files.service import request_upload_url

        db = AsyncMock()
        storage = MagicMock()

        with pytest.raises(ValidationError, match="exceeds"):
            await request_upload_url(
                db=db,
                storage=storage,
                user_id="user-1",
                filename="huge.bin",
                content_type="application/octet-stream",
                size=100 * 1024 * 1024 + 1,  # > 100MB
            )


class TestListFiles:
    async def test_returns_files_and_total(self):
        from app.files.service import list_files

        files = [_make_file_record("f1"), _make_file_record("f2")]
        db = AsyncMock()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2
        list_result = MagicMock()
        list_result.scalars.return_value.all.return_value = files

        db.execute.side_effect = [count_result, list_result]

        result, total = await list_files(db, user_id="user-1", skip=0, limit=20)

        assert total == 2
        assert len(result) == 2

    async def test_empty_list(self):
        from app.files.service import list_files

        db = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        list_result = MagicMock()
        list_result.scalars.return_value.all.return_value = []
        db.execute.side_effect = [count_result, list_result]

        result, total = await list_files(db, user_id="user-1", skip=0, limit=20)

        assert total == 0
        assert result == []


class TestGetDownloadUrl:
    async def test_returns_download_url(self):
        from app.files.service import get_download_url

        file_record = _make_file_record()
        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = file_record
        db.execute.return_value = result

        storage = MagicMock()
        storage.generate_download_url.return_value = "https://s3.example.com/download"

        url = await get_download_url(db, storage, file_id="file-1", user_id="user-1")

        assert url == "https://s3.example.com/download"
        storage.generate_download_url.assert_called_once_with(file_record.storage_key)

    async def test_raises_not_found_for_missing_file(self):
        from app.files.service import get_download_url

        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute.return_value = result

        storage = MagicMock()

        with pytest.raises(NotFoundError):
            await get_download_url(db, storage, file_id="ghost", user_id="user-1")

    async def test_raises_not_found_for_other_users_file(self):
        from app.files.service import get_download_url

        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None  # query filters by user_id
        db.execute.return_value = result

        storage = MagicMock()

        with pytest.raises(NotFoundError):
            await get_download_url(db, storage, file_id="file-1", user_id="other-user")


class TestFilenameSanitization:
    async def test_traversal_attack_stripped_to_basename(self):
        from app.files.service import request_upload_url

        db = AsyncMock()
        storage = MagicMock()
        storage.generate_upload_url.return_value = "https://s3.example.com/signed"

        await request_upload_url(
            db=db,
            storage=storage,
            user_id="user-1",
            filename="../../etc/passwd",
            content_type="text/plain",
            size=100,
        )

        called_key = storage.generate_upload_url.call_args[0][0]
        assert called_key.endswith("/passwd")
        assert "../" not in called_key

    async def test_deep_traversal_stripped(self):
        from app.files.service import request_upload_url

        db = AsyncMock()
        storage = MagicMock()
        storage.generate_upload_url.return_value = "https://s3.example.com/signed"

        await request_upload_url(
            db=db,
            storage=storage,
            user_id="user-1",
            filename="../../../root/.ssh/id_rsa",
            content_type="text/plain",
            size=100,
        )

        called_key = storage.generate_upload_url.call_args[0][0]
        assert called_key.endswith("/id_rsa")
        assert "../" not in called_key

    async def test_normal_filename_unchanged(self):
        from app.files.service import request_upload_url

        db = AsyncMock()
        storage = MagicMock()
        storage.generate_upload_url.return_value = "https://s3.example.com/signed"

        await request_upload_url(
            db=db,
            storage=storage,
            user_id="user-1",
            filename="normal.pdf",
            content_type="application/pdf",
            size=2048,
        )

        called_key = storage.generate_upload_url.call_args[0][0]
        assert called_key.endswith("/normal.pdf")

    async def test_empty_basename_after_sanitization_raises(self):
        from app.files.service import request_upload_url

        db = AsyncMock()
        storage = MagicMock()

        with pytest.raises(ValidationError, match="[Ii]nvalid filename"):
            await request_upload_url(
                db=db,
                storage=storage,
                user_id="user-1",
                filename="../../",
                content_type="text/plain",
                size=100,
            )


class TestDeleteFile:
    async def test_deletes_file_metadata_and_object(self):
        from app.files.service import delete_file

        file_record = _make_file_record()
        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = file_record
        db.execute.return_value = result

        storage = MagicMock()

        await delete_file(db, storage, file_id="file-1", user_id="user-1")

        db.delete.assert_called_once_with(file_record)
        db.commit.assert_awaited_once()
        storage.delete_object.assert_called_once_with(file_record.storage_key)

    async def test_raises_not_found_for_missing_file(self):
        from app.files.service import delete_file

        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute.return_value = result

        storage = MagicMock()

        with pytest.raises(NotFoundError):
            await delete_file(db, storage, file_id="ghost", user_id="user-1")
