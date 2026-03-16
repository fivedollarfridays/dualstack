"""Tests for the initial alembic migration (001_initial_items)."""

from pathlib import Path
from unittest.mock import patch

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

BACKEND_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def alembic_config(tmp_path):
    """Create an alembic config pointing at a temp SQLite database.

    Patches get_database_url so that env.py uses the same temp file
    rather than overriding with in-memory or Turso URLs.
    """
    db_path = tmp_path / "test.db"
    db_url = f"sqlite:///{db_path}"

    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", db_url)
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))

    with patch("app.core.database.get_alembic_database_url", return_value=db_url):
        yield cfg, db_url


def test_upgrade_creates_items_table(alembic_config):
    """Upgrade to head should create the items table."""
    cfg, db_url = alembic_config

    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "items" in tables
    engine.dispose()


def test_items_table_has_correct_columns(alembic_config):
    """Items table should have all expected columns."""
    cfg, db_url = alembic_config

    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("items")}

    expected = {
        "id",
        "user_id",
        "title",
        "description",
        "status",
        "created_at",
        "updated_at",
    }
    assert columns == expected
    engine.dispose()


def test_user_id_index_exists(alembic_config):
    """Items table should have an index on user_id."""
    cfg, db_url = alembic_config

    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    indexes = inspector.get_indexes("items")
    indexed_columns = []
    for idx in indexes:
        indexed_columns.extend(idx["column_names"])

    assert "user_id" in indexed_columns
    engine.dispose()


def test_id_is_primary_key(alembic_config):
    """The id column should be the primary key."""
    cfg, db_url = alembic_config

    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    pk = inspector.get_pk_constraint("items")
    assert "id" in pk["constrained_columns"]
    engine.dispose()


def test_downgrade_removes_items_table(alembic_config):
    """Downgrade to base should remove the items table."""
    cfg, db_url = alembic_config

    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "items" not in tables
    engine.dispose()


def test_upgrade_downgrade_upgrade_is_idempotent(alembic_config):
    """Migration should survive upgrade -> downgrade -> upgrade cycle."""
    cfg, db_url = alembic_config

    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "items" in tables
    engine.dispose()


def test_description_column_is_nullable(alembic_config):
    """The description column should be nullable."""
    cfg, db_url = alembic_config

    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    columns = {col["name"]: col for col in inspector.get_columns("items")}
    assert columns["description"]["nullable"] is True
    engine.dispose()


def test_user_id_column_is_not_nullable(alembic_config):
    """The user_id column should not be nullable."""
    cfg, db_url = alembic_config

    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    columns = {col["name"]: col for col in inspector.get_columns("items")}
    assert columns["user_id"]["nullable"] is False
    engine.dispose()
