"""Tests for items API routes."""

from unittest.mock import patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.auth import get_current_user_id
from app.core.database import Base, get_db
from app.main import app


@pytest_asyncio.fixture
async def test_app():
    """Create a test app with an in-memory database."""
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

    async def override_auth() -> str:
        return "user-1"

    app.dependency_overrides[get_current_user_id] = override_auth

    yield app

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_app):
    """Create an async HTTP client for testing."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


USER_HEADERS = {"x-user-id": "user-1"}


class TestCreateItem:
    """Test POST /api/v1/items."""

    async def test_creates_item_successfully(self, client):
        response = await client.post(
            "/api/v1/items",
            json={"title": "New Item", "description": "A new item"},
            headers=USER_HEADERS,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Item"
        assert data["description"] == "A new item"
        assert data["status"] == "draft"
        assert "user_id" not in data
        assert "id" in data

    async def test_validation_error_missing_title(self, client):
        response = await client.post(
            "/api/v1/items",
            json={"description": "No title"},
            headers=USER_HEADERS,
        )

        assert response.status_code == 422

    async def test_validation_error_empty_title(self, client):
        response = await client.post(
            "/api/v1/items",
            json={"title": ""},
            headers=USER_HEADERS,
        )

        assert response.status_code == 422


class TestListItems:
    """Test GET /api/v1/items."""

    async def test_returns_empty_list(self, client):
        response = await client.get("/api/v1/items", headers=USER_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_returns_created_items(self, client):
        await client.post(
            "/api/v1/items",
            json={"title": "Item 1"},
            headers=USER_HEADERS,
        )
        await client.post(
            "/api/v1/items",
            json={"title": "Item 2"},
            headers=USER_HEADERS,
        )

        response = await client.get("/api/v1/items", headers=USER_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    async def test_pagination(self, client):
        for i in range(5):
            await client.post(
                "/api/v1/items",
                json={"title": f"Item {i}"},
                headers=USER_HEADERS,
            )

        response = await client.get(
            "/api/v1/items?page=2&limit=2", headers=USER_HEADERS
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5


class TestGetItem:
    """Test GET /api/v1/items/{item_id}."""

    async def test_returns_item(self, client):
        create_resp = await client.post(
            "/api/v1/items",
            json={"title": "Find Me"},
            headers=USER_HEADERS,
        )
        item_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/items/{item_id}", headers=USER_HEADERS)

        assert response.status_code == 200
        assert response.json()["title"] == "Find Me"

    async def test_404_for_missing_item(self, client):
        response = await client.get("/api/v1/items/nonexistent", headers=USER_HEADERS)

        assert response.status_code == 404


class TestUpdateItem:
    """Test PATCH /api/v1/items/{item_id}."""

    async def test_updates_item(self, client):
        create_resp = await client.post(
            "/api/v1/items",
            json={"title": "Original"},
            headers=USER_HEADERS,
        )
        item_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/items/{item_id}",
            json={"title": "Updated"},
            headers=USER_HEADERS,
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Updated"

    async def test_404_for_missing_item(self, client):
        response = await client.patch(
            "/api/v1/items/nonexistent",
            json={"title": "Nope"},
            headers=USER_HEADERS,
        )

        assert response.status_code == 404


class TestDeleteItem:
    """Test DELETE /api/v1/items/{item_id}."""

    async def test_deletes_item(self, client):
        create_resp = await client.post(
            "/api/v1/items",
            json={"title": "Delete Me"},
            headers=USER_HEADERS,
        )
        item_id = create_resp.json()["id"]

        response = await client.delete(f"/api/v1/items/{item_id}", headers=USER_HEADERS)

        assert response.status_code == 204

        # Verify it's gone
        get_resp = await client.get(f"/api/v1/items/{item_id}", headers=USER_HEADERS)
        assert get_resp.status_code == 404

    async def test_404_for_missing_item(self, client):
        response = await client.delete(
            "/api/v1/items/nonexistent", headers=USER_HEADERS
        )

        assert response.status_code == 404


class TestReadAuditEvents:
    """NEW-006: Read operations should emit audit events."""

    async def test_list_items_emits_audit(self, client):
        """GET /items should emit log-only audit event with action='list'."""
        with patch(
            "app.items.routes.log_audit_event"
        ) as mock_audit:
            await client.get("/api/v1/items", headers=USER_HEADERS)
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs["action"] == "list"
            assert kwargs["resource_type"] == "item"
            assert kwargs["user_id"] == "user-1"

    async def test_get_item_emits_audit(self, client):
        """GET /items/{id} should emit audit event with action='read'."""
        create_resp = await client.post(
            "/api/v1/items",
            json={"title": "Audit Me"},
            headers=USER_HEADERS,
        )
        item_id = create_resp.json()["id"]

        with patch(
            "app.items.routes.log_audit_event"
        ) as mock_audit:
            await client.get(f"/api/v1/items/{item_id}", headers=USER_HEADERS)
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs["action"] == "read"
            assert kwargs["resource_type"] == "item"
            assert kwargs["resource_id"] == item_id
