"""Tests for items service layer."""

import pytest
import pytest_asyncio

from app.items.models import Item
from app.items.schemas import ItemCreate, ItemUpdate
from app.items.service import create_item, delete_item, get_item, list_items, update_item
from app.core.errors import NotFoundError


class TestCreateItem:
    """Test create_item service function."""

    async def test_returns_item_with_correct_fields(self, db_session):
        data = ItemCreate(title="Test Item", description="desc", status="active")
        item = await create_item(db_session, user_id="user-1", data=data)

        assert isinstance(item, Item)
        assert item.title == "Test Item"
        assert item.description == "desc"
        assert item.status == "active"
        assert item.user_id == "user-1"
        assert item.id is not None

    async def test_default_status_is_draft(self, db_session):
        data = ItemCreate(title="Draft Item")
        item = await create_item(db_session, user_id="user-1", data=data)

        assert item.status == "draft"

    async def test_generates_unique_ids(self, db_session):
        data = ItemCreate(title="Item")
        item1 = await create_item(db_session, user_id="user-1", data=data)
        item2 = await create_item(db_session, user_id="user-1", data=data)

        assert item1.id != item2.id


class TestListItems:
    """Test list_items service function."""

    async def test_returns_empty_list(self, db_session):
        items, total = await list_items(db_session, user_id="user-1")

        assert items == []
        assert total == 0

    async def test_returns_items_for_user(self, db_session):
        data = ItemCreate(title="Item 1")
        await create_item(db_session, user_id="user-1", data=data)
        data = ItemCreate(title="Item 2")
        await create_item(db_session, user_id="user-1", data=data)

        items, total = await list_items(db_session, user_id="user-1")

        assert len(items) == 2
        assert total == 2

    async def test_filters_by_user_id(self, db_session):
        await create_item(
            db_session, user_id="user-1", data=ItemCreate(title="User1 Item")
        )
        await create_item(
            db_session, user_id="user-2", data=ItemCreate(title="User2 Item")
        )

        items, total = await list_items(db_session, user_id="user-1")

        assert len(items) == 1
        assert total == 1
        assert items[0].user_id == "user-1"

    async def test_pagination_skip_and_limit(self, db_session):
        for i in range(5):
            await create_item(
                db_session, user_id="user-1", data=ItemCreate(title=f"Item {i}")
            )

        items, total = await list_items(db_session, user_id="user-1", skip=2, limit=2)

        assert len(items) == 2
        assert total == 5


class TestGetItem:
    """Test get_item service function."""

    async def test_returns_item_when_found(self, db_session):
        created = await create_item(
            db_session, user_id="user-1", data=ItemCreate(title="Find Me")
        )

        found = await get_item(db_session, item_id=created.id, user_id="user-1")

        assert found.id == created.id
        assert found.title == "Find Me"

    async def test_raises_not_found_for_missing_id(self, db_session):
        with pytest.raises(NotFoundError):
            await get_item(db_session, item_id="nonexistent", user_id="user-1")

    async def test_raises_not_found_for_wrong_user(self, db_session):
        created = await create_item(
            db_session, user_id="user-1", data=ItemCreate(title="Private")
        )

        with pytest.raises(NotFoundError):
            await get_item(db_session, item_id=created.id, user_id="user-2")


class TestUpdateItem:
    """Test update_item service function."""

    async def test_partial_update_title(self, db_session):
        created = await create_item(
            db_session,
            user_id="user-1",
            data=ItemCreate(title="Original", description="Keep this"),
        )

        updated = await update_item(
            db_session,
            item_id=created.id,
            user_id="user-1",
            data=ItemUpdate(title="Updated"),
        )

        assert updated.title == "Updated"
        assert updated.description == "Keep this"

    async def test_partial_update_status(self, db_session):
        created = await create_item(
            db_session, user_id="user-1", data=ItemCreate(title="My Item")
        )

        updated = await update_item(
            db_session,
            item_id=created.id,
            user_id="user-1",
            data=ItemUpdate(status="active"),
        )

        assert updated.status == "active"
        assert updated.title == "My Item"

    async def test_raises_not_found_for_missing_id(self, db_session):
        with pytest.raises(NotFoundError):
            await update_item(
                db_session,
                item_id="nonexistent",
                user_id="user-1",
                data=ItemUpdate(title="Nope"),
            )

    async def test_raises_not_found_for_wrong_user(self, db_session):
        created = await create_item(
            db_session, user_id="user-1", data=ItemCreate(title="Private")
        )

        with pytest.raises(NotFoundError):
            await update_item(
                db_session,
                item_id=created.id,
                user_id="user-2",
                data=ItemUpdate(title="Hacked"),
            )


class TestDeleteItem:
    """Test delete_item service function."""

    async def test_deletes_item_successfully(self, db_session):
        created = await create_item(
            db_session, user_id="user-1", data=ItemCreate(title="Delete Me")
        )

        await delete_item(db_session, item_id=created.id, user_id="user-1")

        with pytest.raises(NotFoundError):
            await get_item(db_session, item_id=created.id, user_id="user-1")

    async def test_raises_not_found_for_missing_id(self, db_session):
        with pytest.raises(NotFoundError):
            await delete_item(db_session, item_id="nonexistent", user_id="user-1")

    async def test_raises_not_found_for_wrong_user(self, db_session):
        created = await create_item(
            db_session, user_id="user-1", data=ItemCreate(title="Private")
        )

        with pytest.raises(NotFoundError):
            await delete_item(db_session, item_id=created.id, user_id="user-2")
