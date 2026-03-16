"""Tests for items sort and filter functionality."""

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


def _make_item(title: str, status: str = "draft") -> MagicMock:
    item = MagicMock()
    item.id = f"id-{title.lower().replace(' ', '-')}"
    item.user_id = "user-1"
    item.title = title
    item.description = None
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


class TestSort:
    async def test_sort_by_title_asc(self):
        items = [_make_item("Alpha"), _make_item("Beta")]
        app = _create_app(_mock_db_for_list(items, 2))
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/items?sort_by=title&sort_dir=asc",
                    headers={"x-user-id": "user-1"},
                )
        assert r.status_code == 200
        assert r.json()["total"] == 2

    async def test_sort_by_created_at_desc_default(self):
        items = [_make_item("Item")]
        app = _create_app(_mock_db_for_list(items, 1))
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/items",
                    headers={"x-user-id": "user-1"},
                )
        assert r.status_code == 200

    async def test_invalid_sort_field_returns_422(self):
        app = _create_app(_mock_db_for_list([], 0))
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/items?sort_by=invalid_field",
                    headers={"x-user-id": "user-1"},
                )
        assert r.status_code == 422

    async def test_invalid_sort_dir_returns_422(self):
        app = _create_app(_mock_db_for_list([], 0))
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/items?sort_dir=sideways",
                    headers={"x-user-id": "user-1"},
                )
        assert r.status_code == 422


class TestFilter:
    async def test_filter_by_status(self):
        items = [_make_item("Active One", status="active")]
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

    async def test_combined_search_sort_filter(self):
        """Search + sort + filter + pagination work together."""
        items = [_make_item("Widget", status="active")]
        app = _create_app(_mock_db_for_list(items, 1))
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/items?search=widget&sort_by=title&sort_dir=asc&status=active&page=1&limit=10",
                    headers={"x-user-id": "user-1"},
                )
        assert r.status_code == 200
        assert r.json()["total"] == 1
