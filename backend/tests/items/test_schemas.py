"""Tests for items schema validation."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.items.schemas import ItemCreate, ItemResponse, ItemUpdate
from app.items.models import ItemStatus


class TestItemStatus:
    """Test the ItemStatus enum values."""

    def test_draft_value(self):
        assert ItemStatus.DRAFT == "draft"

    def test_active_value(self):
        assert ItemStatus.ACTIVE == "active"

    def test_archived_value(self):
        assert ItemStatus.ARCHIVED == "archived"

    def test_all_values(self):
        values = [s.value for s in ItemStatus]
        assert values == ["draft", "active", "archived"]


class TestItemCreate:
    """Test ItemCreate schema validation."""

    def test_valid_minimal(self):
        item = ItemCreate(title="My Item")
        assert item.title == "My Item"
        assert item.description is None
        assert item.status == "draft"

    def test_valid_full(self):
        item = ItemCreate(
            title="My Item",
            description="A description",
            status="active",
        )
        assert item.title == "My Item"
        assert item.description == "A description"
        assert item.status == "active"

    def test_missing_title_raises(self):
        with pytest.raises(ValidationError):
            ItemCreate()

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError):
            ItemCreate(title="")

    def test_title_too_long_raises(self):
        with pytest.raises(ValidationError):
            ItemCreate(title="x" * 256)

    def test_title_max_length_ok(self):
        item = ItemCreate(title="x" * 255)
        assert len(item.title) == 255

    def test_description_max_length_ok(self):
        """ItemCreate should accept description up to 10000 chars."""
        item = ItemCreate(title="X", description="a" * 10000)
        assert len(item.description) == 10000

    def test_description_too_long_raises(self):
        """ItemCreate should reject description over 10000 chars."""
        with pytest.raises(ValidationError):
            ItemCreate(title="X", description="a" * 10001)

    def test_rejects_invalid_status(self):
        """ItemCreate should reject status values outside the allowed literal."""
        with pytest.raises(ValidationError):
            ItemCreate(title="X", status="invalid")

    def test_accepts_valid_statuses(self):
        """ItemCreate should accept all three valid status values."""
        for status in ("draft", "active", "archived"):
            item = ItemCreate(title="X", status=status)
            assert item.status == status


class TestItemUpdate:
    """Test ItemUpdate schema validation (all fields optional)."""

    def test_empty_update(self):
        item = ItemUpdate()
        assert item.title is None
        assert item.description is None
        assert item.status is None

    def test_partial_update_title_only(self):
        item = ItemUpdate(title="New Title")
        assert item.title == "New Title"
        assert item.description is None
        assert item.status is None

    def test_partial_update_status_only(self):
        item = ItemUpdate(status="archived")
        assert item.status == "archived"
        assert item.title is None

    def test_title_too_long_raises(self):
        with pytest.raises(ValidationError):
            ItemUpdate(title="x" * 256)

    def test_description_max_length_ok(self):
        """ItemUpdate should accept description up to 10000 chars."""
        item = ItemUpdate(description="b" * 10000)
        assert len(item.description) == 10000

    def test_description_too_long_raises(self):
        """ItemUpdate should reject description over 10000 chars."""
        with pytest.raises(ValidationError):
            ItemUpdate(description="b" * 10001)

    def test_rejects_invalid_status(self):
        """ItemUpdate should reject status values outside the allowed literal."""
        with pytest.raises(ValidationError):
            ItemUpdate(status="bogus")


class TestItemResponse:
    """Test ItemResponse model construction."""

    def test_from_dict(self):
        now = datetime(2026, 1, 1, 12, 0, 0)
        resp = ItemResponse(
            id="abc-123",
            title="Test Item",
            description="A test",
            status="draft",
            created_at=now,
            updated_at=now,
        )
        assert resp.id == "abc-123"
        assert resp.title == "Test Item"
        assert resp.description == "A test"
        assert resp.status == "draft"
        assert resp.created_at == now
        assert resp.updated_at == now

    def test_does_not_include_user_id(self):
        """SEC-002: ItemResponse must not expose user_id."""
        assert "user_id" not in ItemResponse.model_fields

    def test_model_config_from_attributes(self):
        """ItemResponse should support from_attributes for ORM model conversion."""
        assert ItemResponse.model_config.get("from_attributes") is True
