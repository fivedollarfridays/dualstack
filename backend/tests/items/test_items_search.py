"""Tests for items search functionality."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.exception_handlers import register_exception_handlers
from app.items.routes import router as items_router


def _mock_settings():
    s = MagicMock()
    s.clerk_jwks_url = ""
    s.environment = "development"
    return s


def _make_item(
    title: str, description: str | None = None, status: str = "draft"
) -> MagicMock:
    item = MagicMock()
    item.id = f"id-{title.lower().replace(' ', '-')}"
    item.user_id = "user-1"
    item.title = title
    item.description = description
    item.status = status
    item.created_at = datetime(2026, 1, 1)
    item.updated_at = datetime(2026, 1, 1)
    return item


def _mock_db_for_list(items: list, total: int):
    mock_session = AsyncMock()
    count_result = MagicMock()
    count_result.scalar_one.return_value = total
    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = items
    mock_session.execute.side_effect = [count_result, list_result]

    async def override():
        yield mock_session

    return override


def _create_app(mock_db_factory):
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(items_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = mock_db_factory
    return app


class TestSearch:
    async def test_search_returns_matching_items(self):
        items = [_make_item("My Widget")]
        app = _create_app(_mock_db_for_list(items, 1))
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/items?search=widget",
                    headers={"x-user-id": "user-1"},
                )
        assert r.status_code == 200
        assert r.json()["total"] == 1

    async def test_search_empty_returns_all(self):
        items = [_make_item("A"), _make_item("B")]
        app = _create_app(_mock_db_for_list(items, 2))
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/items",
                    headers={"x-user-id": "user-1"},
                )
        assert r.status_code == 200
        assert r.json()["total"] == 2

    async def test_search_no_matches(self):
        app = _create_app(_mock_db_for_list([], 0))
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/items?search=nonexistent",
                    headers={"x-user-id": "user-1"},
                )
        assert r.status_code == 200
        assert r.json()["total"] == 0
        assert r.json()["items"] == []

    async def test_search_with_status_filter(self):
        items = [_make_item("Active Item", status="active")]
        app = _create_app(_mock_db_for_list(items, 1))
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/items?status=active",
                    headers={"x-user-id": "user-1"},
                )
        assert r.status_code == 200
        assert r.json()["total"] == 1
