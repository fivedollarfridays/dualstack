"""Tests for admin service — user listing, role assignment, health check."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.admin.service import assign_role, get_health, list_users
from app.core.errors import NotFoundError, ValidationError


def _make_user(clerk_id: str, role: str = "member") -> MagicMock:
    user = MagicMock()
    user.id = f"id-{clerk_id}"
    user.clerk_user_id = clerk_id
    user.role = role
    user.subscription_plan = "free"
    user.subscription_status = "none"
    user.created_at = datetime(2026, 1, 1)
    user.updated_at = datetime(2026, 1, 1)
    return user


def _mock_db_for_list(users: list, total: int) -> AsyncMock:
    """Mock DB session for list_users queries."""
    db = AsyncMock()

    count_result = MagicMock()
    count_result.scalar_one.return_value = total

    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = users

    db.execute.side_effect = [count_result, list_result]
    return db


def _mock_db_for_get(user: MagicMock | None) -> AsyncMock:
    """Mock DB session for single-user lookup."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    db.execute.return_value = result
    return db


class TestListUsers:
    async def test_returns_users_and_total(self):
        users = [_make_user("u1"), _make_user("u2")]
        db = _mock_db_for_list(users, total=2)

        result, total = await list_users(db, skip=0, limit=20)

        assert total == 2
        assert len(result) == 2

    async def test_empty_list(self):
        db = _mock_db_for_list([], total=0)

        result, total = await list_users(db, skip=0, limit=20)

        assert total == 0
        assert result == []

    async def test_search_filter(self):
        users = [_make_user("matching-user")]
        db = _mock_db_for_list(users, total=1)

        result, total = await list_users(db, skip=0, limit=20, search="matching")

        assert total == 1
        # Verify that execute was called (the search term is in the query)
        assert db.execute.call_count == 2


class TestAssignRole:
    async def test_assigns_admin_role(self):
        user = _make_user("u1", role="member")
        db = _mock_db_for_get(user)

        updated = await assign_role(db, user_id="id-u1", role="admin")

        assert updated.role == "admin"
        db.commit.assert_awaited_once()

    async def test_assigns_member_role(self):
        user = _make_user("u1", role="admin")
        db = AsyncMock()

        # First execute: user lookup
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = user

        # Second execute: admin count (more than 1 so demotion is allowed)
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        db.execute.side_effect = [user_result, count_result]

        updated = await assign_role(db, user_id="id-u1", role="member")

        assert updated.role == "member"

    async def test_raises_not_found_for_missing_user(self):
        db = _mock_db_for_get(None)

        with pytest.raises(NotFoundError):
            await assign_role(db, user_id="ghost", role="admin")

    async def test_raises_validation_error_for_invalid_role(self):
        user = _make_user("u1")
        db = _mock_db_for_get(user)

        with pytest.raises(ValidationError):
            await assign_role(db, user_id="id-u1", role="superadmin")

    async def test_prevents_demoting_last_admin(self):
        user = _make_user("u1", role="admin")
        db = AsyncMock()

        # First execute: user lookup
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = user

        # Second execute: admin count
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        db.execute.side_effect = [user_result, count_result]

        with pytest.raises(ValidationError, match="last admin"):
            await assign_role(db, user_id="id-u1", role="member")


class TestGetHealth:
    async def test_returns_health_dict(self):
        db = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 42
        db.execute.return_value = count_result

        health = await get_health(db)

        assert health["status"] == "healthy"
        assert health["user_count"] == 42
        assert "database" in health

    async def test_unhealthy_on_db_error(self):
        db = AsyncMock()
        db.execute.side_effect = Exception("connection refused")

        health = await get_health(db)

        assert health["status"] == "unhealthy"
        assert health["database"] == "error"
