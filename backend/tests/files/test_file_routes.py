"""Tests for file upload API routes."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.auth import get_current_user_id
from app.core.database import Base, get_db
from app.core.storage import StorageService
from app.files.routes import _get_storage
from app.main import app


@pytest_asyncio.fixture
async def mock_storage():
    """Create a mock storage service."""
    storage = MagicMock(spec=StorageService)
    storage.bucket = "test-bucket"
    storage.generate_upload_url.return_value = "https://s3.example.com/presigned-upload"
    storage.generate_download_url.return_value = (
        "https://s3.example.com/presigned-download"
    )
    return storage


@pytest_asyncio.fixture
async def test_app(mock_storage):
    """Create a test app with in-memory database and mocked storage."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[_get_storage] = lambda: mock_storage

    yield app

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestUploadUrl:
    async def test_returns_presigned_url_and_file_id(self, client):
        response = await client.post(
            "/api/v1/files/upload-url",
            json={"filename": "photo.png", "content_type": "image/png", "size": 2048},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["upload_url"] == "https://s3.example.com/presigned-upload"
        assert "file_id" in data
        assert "storage_key" not in data

    async def test_rejects_missing_filename(self, client):
        response = await client.post(
            "/api/v1/files/upload-url",
            json={"content_type": "image/png", "size": 1024},
        )
        assert response.status_code == 422

    async def test_rejects_oversized_file(self, client):
        response = await client.post(
            "/api/v1/files/upload-url",
            json={
                "filename": "big.png",
                "content_type": "image/png",
                "size": 200_000_000,
            },
        )
        assert response.status_code == 422


class TestContentTypeValidationRoute:
    async def test_rejects_text_html(self, client):
        response = await client.post(
            "/api/v1/files/upload-url",
            json={"filename": "xss.html", "content_type": "text/html", "size": 100},
        )
        assert response.status_code == 422

    async def test_rejects_svg_xml(self, client):
        response = await client.post(
            "/api/v1/files/upload-url",
            json={"filename": "xss.svg", "content_type": "image/svg+xml", "size": 100},
        )
        assert response.status_code == 422

    async def test_accepts_image_png(self, client):
        response = await client.post(
            "/api/v1/files/upload-url",
            json={"filename": "ok.png", "content_type": "image/png", "size": 100},
        )
        assert response.status_code == 201


class TestListFiles:
    async def test_returns_empty_list_initially(self, client):
        response = await client.get("/api/v1/files")
        assert response.status_code == 200
        data = response.json()
        assert data["files"] == []
        assert data["total"] == 0

    async def test_returns_uploaded_files(self, client):
        # Upload a file first
        await client.post(
            "/api/v1/files/upload-url",
            json={"filename": "photo.png", "content_type": "image/png", "size": 1024},
        )

        response = await client.get("/api/v1/files")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["files"][0]["filename"] == "photo.png"


class TestDownloadUrl:
    async def test_returns_download_url(self, client):
        # Upload first
        upload = await client.post(
            "/api/v1/files/upload-url",
            json={
                "filename": "doc.pdf",
                "content_type": "application/pdf",
                "size": 512,
            },
        )
        file_id = upload.json()["file_id"]

        response = await client.get(f"/api/v1/files/{file_id}/download-url")
        assert response.status_code == 200
        assert (
            response.json()["download_url"]
            == "https://s3.example.com/presigned-download"
        )

    async def test_returns_404_for_nonexistent_file(self, client):
        response = await client.get(
            "/api/v1/files/00000000-0000-0000-0000-000000000000/download-url"
        )
        assert response.status_code == 404


class TestDeleteFile:
    async def test_deletes_file(self, client, mock_storage):
        upload = await client.post(
            "/api/v1/files/upload-url",
            json={"filename": "temp.txt", "content_type": "text/plain", "size": 64},
        )
        file_id = upload.json()["file_id"]

        response = await client.delete(f"/api/v1/files/{file_id}")
        assert response.status_code == 204

        mock_storage.delete_object.assert_called_once()

        # Verify file is gone
        list_resp = await client.get("/api/v1/files")
        assert list_resp.json()["total"] == 0

    async def test_returns_404_for_nonexistent_file(self, client):
        response = await client.delete(
            "/api/v1/files/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404


class TestFileIdUuidValidation:
    """file_id path params must be valid UUID format."""

    async def test_download_url_rejects_non_uuid(self, client):
        """GET /files/{file_id}/download-url rejects non-UUID file_id with 422."""
        response = await client.get("/api/v1/files/not-a-uuid/download-url")
        assert response.status_code == 422

    async def test_delete_rejects_non_uuid(self, client):
        """DELETE /files/{file_id} rejects non-UUID file_id with 422."""
        response = await client.delete("/api/v1/files/not-a-uuid")
        assert response.status_code == 422

    async def test_download_url_accepts_valid_uuid(self, client):
        """GET /files/{file_id}/download-url accepts valid UUID format (may 404)."""
        response = await client.get(
            "/api/v1/files/12345678-1234-1234-1234-123456789abc/download-url"
        )
        # Valid UUID format is accepted (404 because file doesn't exist)
        assert response.status_code == 404

    async def test_delete_accepts_valid_uuid(self, client):
        """DELETE /files/{file_id} accepts valid UUID format (may 404)."""
        response = await client.delete(
            "/api/v1/files/12345678-1234-1234-1234-123456789abc"
        )
        assert response.status_code == 404


class TestFileRouteAuditEvents:
    """Audit events are persisted for file read routes."""

    async def test_list_files_logs_audit_event(self, client):
        """GET /files emits a log-only 'list' audit event."""
        with patch(
            "app.files.routes.log_audit_event",
        ) as mock_audit:
            await client.get("/api/v1/files")
            mock_audit.assert_called_once()
            call_kwargs = mock_audit.call_args
            assert call_kwargs.kwargs["action"] == "list"
            assert call_kwargs.kwargs["resource_type"] == "file"
            assert call_kwargs.kwargs["user_id"] == "user-1"

    async def test_download_url_persists_audit_event(self, client):
        """GET /files/{id}/download-url emits a 'download_request' audit event."""
        # Upload a file first so we have a valid file_id
        upload = await client.post(
            "/api/v1/files/upload-url",
            json={"filename": "audit.txt", "content_type": "text/plain", "size": 64},
        )
        file_id = upload.json()["file_id"]

        with patch(
            "app.files.routes.persist_audit_event",
            new_callable=AsyncMock,
        ) as mock_audit:
            response = await client.get(f"/api/v1/files/{file_id}/download-url")
            assert response.status_code == 200
            mock_audit.assert_called_once()
            call_kwargs = mock_audit.call_args
            assert call_kwargs.kwargs["action"] == "download_request"
            assert call_kwargs.kwargs["resource_type"] == "file"
            assert call_kwargs.kwargs["resource_id"] == file_id
            assert call_kwargs.kwargs["user_id"] == "user-1"
