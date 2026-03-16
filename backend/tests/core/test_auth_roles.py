"""Tests for RBAC FastAPI dependencies (require_role, require_permission)."""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.exception_handlers import register_exception_handlers
from app.core.rbac import Role, require_permission, require_role


def _mock_settings():
    settings = MagicMock()
    settings.clerk_jwks_url = ""
    settings.environment = "development"
    return settings


def _make_mock_db(role: str | None):
    """Return an async generator that yields a mock session.

    The session's execute().scalar_one_or_none() returns a User-like
    object with the given role, or None if role is None.
    """
    user_obj = None
    if role is not None:
        user_obj = MagicMock()
        user_obj.role = role

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user_obj

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    async def override_get_db():
        yield mock_session

    return override_get_db


def _create_role_app(role: str | None) -> FastAPI:
    """App with admin-only and member-ok endpoints, DB mocked for given role."""
    app = FastAPI()
    register_exception_handlers(app)
    app.dependency_overrides[get_db] = _make_mock_db(role)

    @app.get("/admin-only")
    async def admin_only(user_id: str = Depends(require_role(Role.ADMIN))):
        return {"user_id": user_id}

    @app.get("/member-ok")
    async def member_ok(user_id: str = Depends(require_role(Role.MEMBER))):
        return {"user_id": user_id}

    @app.get("/manage-users")
    async def manage_users(
        user_id: str = Depends(require_permission("users:manage")),
    ):
        return {"user_id": user_id}

    @app.get("/read-profile")
    async def read_profile(
        user_id: str = Depends(require_permission("profile:read")),
    ):
        return {"user_id": user_id}

    return app


class TestRequireRole:
    """require_role() FastAPI dependency."""

    async def test_admin_accesses_admin_only(self):
        app = _create_role_app("admin")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get("/admin-only", headers={"x-user-id": "user-admin"})
        assert r.status_code == 200
        assert r.json()["user_id"] == "user-admin"

    async def test_member_rejected_from_admin_only(self):
        app = _create_role_app("member")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/admin-only", headers={"x-user-id": "user-member"}
                )
        assert r.status_code == 403

    async def test_admin_accesses_member_endpoint(self):
        app = _create_role_app("admin")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get("/member-ok", headers={"x-user-id": "user-admin"})
        assert r.status_code == 200

    async def test_member_accesses_member_endpoint(self):
        app = _create_role_app("member")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get("/member-ok", headers={"x-user-id": "user-member"})
        assert r.status_code == 200

    async def test_unknown_user_returns_403(self):
        app = _create_role_app(None)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get("/admin-only", headers={"x-user-id": "ghost"})
        assert r.status_code == 403

    async def test_unauthenticated_returns_401(self):
        """No X-User-ID header → auth fails before role check."""
        app = _create_role_app("admin")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get("/admin-only")
        assert r.status_code == 401


class TestRequirePermission:
    """require_permission() FastAPI dependency."""

    async def test_admin_has_users_manage(self):
        app = _create_role_app("admin")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/manage-users", headers={"x-user-id": "user-admin"}
                )
        assert r.status_code == 200

    async def test_member_lacks_users_manage(self):
        app = _create_role_app("member")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/manage-users", headers={"x-user-id": "user-member"}
                )
        assert r.status_code == 403

    async def test_member_has_profile_read(self):
        app = _create_role_app("member")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/read-profile", headers={"x-user-id": "user-member"}
                )
        assert r.status_code == 200

    async def test_unknown_user_returns_403(self):
        app = _create_role_app(None)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get("/read-profile", headers={"x-user-id": "ghost"})
        assert r.status_code == 403
