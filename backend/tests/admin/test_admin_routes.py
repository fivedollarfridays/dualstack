"""Tests for admin API routes — RBAC protection, user management, health, audit."""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.admin.routes import router as admin_router
from app.core.database import get_db
from app.core.exception_handlers import register_exception_handlers


def _mock_settings():
    settings = MagicMock()
    settings.clerk_jwks_url = ""
    settings.environment = "development"
    return settings


def _make_user_row(user_id: str, clerk_id: str, role: str) -> MagicMock:
    from datetime import datetime

    user = MagicMock()
    user.id = user_id
    user.clerk_user_id = clerk_id
    user.role = role
    user.subscription_plan = "free"
    user.subscription_status = "none"
    user.created_at = datetime(2026, 1, 1)
    user.updated_at = datetime(2026, 1, 1)
    return user


def _make_mock_db(caller_role: str | None):
    """Mock DB: first execute resolves the caller's role (for RBAC),
    subsequent calls are for the actual service logic."""
    caller = None
    if caller_role is not None:
        caller = MagicMock()
        caller.role = caller_role

    role_result = MagicMock()
    role_result.scalar_one_or_none.return_value = caller

    mock_session = AsyncMock()
    # Default: return the role lookup result for RBAC check
    mock_session.execute.return_value = role_result
    return mock_session


def _create_admin_app(mock_db_factory):
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(admin_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = mock_db_factory
    return app


class TestRBACProtection:
    """Admin endpoints must return 403 for non-admin users."""

    def _make_app(self, role: str | None):
        mock_db = _make_mock_db(role)

        async def override():
            yield mock_db

        return _create_admin_app(override)

    async def test_member_gets_403_on_users(self):
        app = self._make_app("member")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/admin/users",
                    headers={"x-user-id": "user-member"},
                )
        assert r.status_code == 403

    async def test_member_gets_403_on_health(self):
        app = self._make_app("member")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/admin/health",
                    headers={"x-user-id": "user-member"},
                )
        assert r.status_code == 403

    async def test_member_gets_403_on_audit(self):
        app = self._make_app("member")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/admin/audit",
                    headers={"x-user-id": "user-member"},
                )
        assert r.status_code == 403

    async def test_member_gets_403_on_role_update(self):
        app = self._make_app("member")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.patch(
                    "/api/v1/admin/users/some-id/role",
                    json={"role": "admin"},
                    headers={"x-user-id": "user-member"},
                )
        assert r.status_code == 403

    async def test_unauthenticated_gets_401(self):
        app = self._make_app("admin")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get("/api/v1/admin/users")
        assert r.status_code == 401


class TestAdminUsersEndpoint:
    """GET /api/v1/admin/users — admin-only user listing."""

    async def test_admin_gets_user_list(self):
        users = [
            _make_user_row("id-1", "clerk-1", "member"),
            _make_user_row("id-2", "clerk-2", "admin"),
        ]
        mock_db = AsyncMock()

        # Call 1: RBAC role lookup → admin
        admin_caller = MagicMock()
        admin_caller.role = "admin"
        rbac_result = MagicMock()
        rbac_result.scalar_one_or_none.return_value = admin_caller

        # Call 2: count query
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        # Call 3: user list query
        list_result = MagicMock()
        list_result.scalars.return_value.all.return_value = users

        mock_db.execute.side_effect = [rbac_result, count_result, list_result]

        async def override():
            yield mock_db

        app = _create_admin_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/admin/users",
                    headers={"x-user-id": "clerk-admin"},
                )
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 2
        assert len(data["users"]) == 2

    async def test_admin_gets_user_list_with_search(self):
        mock_db = AsyncMock()

        admin_caller = MagicMock()
        admin_caller.role = "admin"
        rbac_result = MagicMock()
        rbac_result.scalar_one_or_none.return_value = admin_caller

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        list_result = MagicMock()
        list_result.scalars.return_value.all.return_value = []

        mock_db.execute.side_effect = [rbac_result, count_result, list_result]

        async def override():
            yield mock_db

        app = _create_admin_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/admin/users?search=nobody",
                    headers={"x-user-id": "clerk-admin"},
                )
        assert r.status_code == 200
        assert r.json()["total"] == 0


class TestAdminRoleUpdate:
    """PATCH /api/v1/admin/users/{id}/role — role assignment."""

    async def test_admin_assigns_role(self):
        target_user = _make_user_row("id-target", "clerk-target", "member")
        mock_db = AsyncMock()

        admin_caller = MagicMock()
        admin_caller.role = "admin"
        rbac_result = MagicMock()
        rbac_result.scalar_one_or_none.return_value = admin_caller

        target_result = MagicMock()
        target_result.scalar_one_or_none.return_value = target_user

        mock_db.execute.side_effect = [rbac_result, target_result]

        async def override():
            yield mock_db

        app = _create_admin_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.patch(
                    "/api/v1/admin/users/id-target/role",
                    json={"role": "admin"},
                    headers={"x-user-id": "clerk-admin"},
                )
        assert r.status_code == 200
        assert r.json()["role"] == "admin"


class TestAdminHealthEndpoint:
    """GET /api/v1/admin/health — system health for admins."""

    async def test_admin_gets_health(self):
        mock_db = AsyncMock()

        admin_caller = MagicMock()
        admin_caller.role = "admin"
        rbac_result = MagicMock()
        rbac_result.scalar_one_or_none.return_value = admin_caller

        count_result = MagicMock()
        count_result.scalar_one.return_value = 10

        mock_db.execute.side_effect = [rbac_result, count_result]

        async def override():
            yield mock_db

        app = _create_admin_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/admin/health",
                    headers={"x-user-id": "clerk-admin"},
                )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert data["user_count"] == 10


class TestAdminAuditEndpoint:
    """GET /api/v1/admin/audit — paginated audit log."""

    async def test_admin_gets_audit_log(self):
        mock_db = AsyncMock()

        admin_caller = MagicMock()
        admin_caller.role = "admin"
        rbac_result = MagicMock()
        rbac_result.scalar_one_or_none.return_value = admin_caller

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        list_result = MagicMock()
        list_result.scalars.return_value.all.return_value = []

        mock_db.execute.side_effect = [rbac_result, count_result, list_result]

        async def override():
            yield mock_db

        app = _create_admin_app(override)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            with patch("app.core.auth.get_settings", return_value=_mock_settings()):
                r = await client.get(
                    "/api/v1/admin/audit",
                    headers={"x-user-id": "clerk-admin"},
                )
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["entries"] == []
