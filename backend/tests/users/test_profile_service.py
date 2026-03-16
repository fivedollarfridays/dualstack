"""Tests for user profile service — get, update, delete."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.errors import NotFoundError
from app.users.profile_service import delete_account, update_profile
from app.users.service import get_user_by_clerk_id


def _make_user(clerk_id: str = "clerk-1", display_name: str | None = None) -> MagicMock:
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


def _mock_db_with_user(user: MagicMock | None) -> AsyncMock:
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    db.execute.return_value = result
    return db


class TestGetProfile:
    async def test_returns_profile_for_existing_user(self):
        user = _make_user("clerk-1", display_name="Alice")
        db = _mock_db_with_user(user)

        profile = await get_user_by_clerk_id(db, "clerk-1")

        assert profile.clerk_user_id == "clerk-1"
        assert profile.display_name == "Alice"

    async def test_returns_none_for_missing_user(self):
        db = _mock_db_with_user(None)

        profile = await get_user_by_clerk_id(db, "ghost")

        assert profile is None


class TestUpdateProfile:
    async def test_updates_display_name(self):
        user = _make_user("clerk-1")
        db = _mock_db_with_user(user)

        updated = await update_profile(db, "clerk-1", display_name="Bob")

        assert updated.display_name == "Bob"
        db.commit.assert_awaited_once()

    async def test_updates_avatar_url(self):
        user = _make_user("clerk-1")
        db = _mock_db_with_user(user)

        updated = await update_profile(
            db, "clerk-1", avatar_url="https://img.example.com/a.png"
        )

        assert updated.avatar_url == "https://img.example.com/a.png"

    async def test_raises_not_found_for_missing_user(self):
        db = _mock_db_with_user(None)

        with pytest.raises(NotFoundError):
            await update_profile(db, "ghost", display_name="Nobody")

    async def test_skips_none_fields(self):
        user = _make_user("clerk-1", display_name="Alice")
        db = _mock_db_with_user(user)

        await update_profile(db, "clerk-1", display_name=None, avatar_url=None)

        # display_name should remain unchanged
        assert user.display_name == "Alice"


class TestDeleteAccount:
    async def test_deletes_existing_user(self):
        user = _make_user("clerk-1")
        db = _mock_db_with_user(user)

        await delete_account(db, "clerk-1")

        db.delete.assert_awaited_once_with(user)
        db.commit.assert_awaited_once()

    async def test_deletes_user_items(self):
        user = _make_user("clerk-1")
        db = _mock_db_with_user(user)

        await delete_account(db, "clerk-1")

        # execute is called twice: once for user lookup, once for item deletion
        assert db.execute.await_count >= 2

    async def test_raises_not_found_for_missing_user(self):
        db = _mock_db_with_user(None)

        with pytest.raises(NotFoundError):
            await delete_account(db, "ghost")
