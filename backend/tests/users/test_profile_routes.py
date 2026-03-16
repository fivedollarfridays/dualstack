"""Tests for profile API routes — GET/PATCH/DELETE /users/me/profile."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.exception_handlers import register_exception_handlers
from app.users.routes import router as users_router


def _mock_settings():
    s = MagicMock()
    s.clerk_jwks_url = ""
    s.environment = "development"
    return s


def _make_user(clerk_id: str, display_name: str | None = None) -> MagicMock:
    user = MagicMock()
    user.id = f"id-{clerk_id}"
    user.clerk_user_id = clerk_id
    user.display_name = display_name
    user.avatar_url = None
    user.role = "member"
    user.subscription_plan = "free"
    user.subscription_status = "none"
    user.created_at = datetime(2026, 1, 1)
    user.updated_at = datetime(2026, 1, 1)
    return user


def _create_app(mock_db_factory):
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(users_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = mock_db_factory
    return app


def _mock_db_returning(user: MagicMock | None):
    mock_session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = result

    async def override():
        yield mock_session

    return override, mock_session


class TestGetProfile:
    async def test_returns_profile(self):
        user = _make_user("clerk-1", display_name="Alice")
        override, _ = _mock_db_returning(user)
        app = _create_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/users/me/profile",
                    headers={"x-user-id": "clerk-1"},
                )
        assert r.status_code == 200
        data = r.json()
        assert data["display_name"] == "Alice"
        assert data["clerk_user_id"] == "clerk-1"

    async def test_returns_404_for_missing_user(self):
        override, _ = _mock_db_returning(None)
        app = _create_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/users/me/profile",
                    headers={"x-user-id": "ghost"},
                )
        assert r.status_code == 404

    async def test_returns_401_without_auth(self):
        override, _ = _mock_db_returning(None)
        app = _create_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get("/api/v1/users/me/profile")
        assert r.status_code == 401


class TestUpdateProfile:
    async def test_updates_display_name(self):
        user = _make_user("clerk-1")
        override, mock_session = _mock_db_returning(user)
        app = _create_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.patch(
                    "/api/v1/users/me/profile",
                    json={"display_name": "Bob"},
                    headers={"x-user-id": "clerk-1"},
                )
        assert r.status_code == 200
        assert user.display_name == "Bob"

    async def test_returns_404_for_missing_user(self):
        override, _ = _mock_db_returning(None)
        app = _create_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.patch(
                    "/api/v1/users/me/profile",
                    json={"display_name": "Nobody"},
                    headers={"x-user-id": "ghost"},
                )
        assert r.status_code == 404


class TestDeleteAccount:
    async def test_deletes_account(self):
        user = _make_user("clerk-1")
        override, mock_session = _mock_db_returning(user)
        app = _create_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.delete(
                    "/api/v1/users/me",
                    headers={
                        "x-user-id": "clerk-1",
                        "x-confirm-delete": "DELETE MY ACCOUNT",
                    },
                )
        assert r.status_code == 204
        mock_session.delete.assert_awaited_once_with(user)

    async def test_requires_confirmation_header(self):
        user = _make_user("clerk-1")
        override, _ = _mock_db_returning(user)
        app = _create_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.delete(
                    "/api/v1/users/me",
                    headers={"x-user-id": "clerk-1"},
                )
        assert r.status_code == 400

    async def test_rejects_wrong_confirmation(self):
        user = _make_user("clerk-1")
        override, _ = _mock_db_returning(user)
        app = _create_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.delete(
                    "/api/v1/users/me",
                    headers={
                        "x-user-id": "clerk-1",
                        "x-confirm-delete": "maybe",
                    },
                )
        assert r.status_code == 400
