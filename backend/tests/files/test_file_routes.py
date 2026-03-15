"""Tests for file upload API routes."""

from unittest.mock import MagicMock, patch

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
    storage.generate_download_url.return_value = "https://s3.example.com/presigned-download"
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
        assert "storage_key" in data

    async def test_rejects_missing_filename(self, client):
        response = await client.post(
            "/api/v1/files/upload-url",
            json={"content_type": "image/png", "size": 1024},
        )
        assert response.status_code == 422

    async def test_rejects_oversized_file(self, client):
        response = await client.post(
            "/api/v1/files/upload-url",
            json={"filename": "big.bin", "content_type": "application/octet-stream", "size": 200_000_000},
        )
        assert response.status_code == 400


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
            json={"filename": "doc.pdf", "content_type": "application/pdf", "size": 512},
        )
        file_id = upload.json()["file_id"]

        response = await client.get(f"/api/v1/files/{file_id}/download-url")
        assert response.status_code == 200
        assert response.json()["download_url"] == "https://s3.example.com/presigned-download"

    async def test_returns_404_for_nonexistent_file(self, client):
        response = await client.get("/api/v1/files/nonexistent/download-url")
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
        response = await client.delete("/api/v1/files/nonexistent")
        assert response.status_code == 404
