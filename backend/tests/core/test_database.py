"""Tests for app.core.database module."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

import app.core.database as db_module
from app.core.database import (
    Base,
    get_database_url,
    get_engine,
    get_async_session_factory,
    get_db,
    init_db,
    close_db,
    reset_engine,
    _register_query_metrics_listeners,
    enable_query_metrics_for_testing,
)


class TestBase:
    """Test the Base declarative model class."""

    def test_base_is_declarative_base(self):
        """Base should be a subclass of DeclarativeBase."""
        assert issubclass(Base, DeclarativeBase)

    def test_base_has_metadata(self):
        """Base should have metadata attribute."""
        assert hasattr(Base, "metadata")


class TestGetDatabaseUrl:
    """Test get_database_url function."""

    def test_returns_memory_sqlite_when_no_turso_url(self):
        """Without turso_database_url, should return in-memory SQLite URL."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(turso_database_url="")
            url = get_database_url()
            assert url == "sqlite+aiosqlite:///:memory:"

    def test_returns_local_sqlite_for_libsql_url(self):
        """With libsql:// URL, should convert to local SQLite URL."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(
                turso_database_url="libsql://my-db.turso.io"
            )
            url = get_database_url()
            assert url == "sqlite+aiosqlite:///./dualstack.db"

    def test_returns_url_as_is_for_non_libsql(self):
        """With non-libsql URL, should return it directly."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(
                turso_database_url="sqlite+aiosqlite:///./test.db"
            )
            url = get_database_url()
            assert url == "sqlite+aiosqlite:///./test.db"


class TestGetEngine:
    """Test get_engine function."""

    def setup_method(self):
        """Reset engine state before each test."""
        reset_engine()

    def teardown_method(self):
        """Reset engine state after each test."""
        reset_engine()

    def test_get_engine_creates_engine(self):
        """get_engine should create and return an async engine."""
        with patch("app.core.database.get_database_url") as mock_url:
            mock_url.return_value = "sqlite+aiosqlite:///:memory:"
            engine = get_engine()
            assert engine is not None

    def test_get_engine_returns_same_instance(self):
        """get_engine should return the same engine on repeated calls."""
        with patch("app.core.database.get_database_url") as mock_url:
            mock_url.return_value = "sqlite+aiosqlite:///:memory:"
            engine1 = get_engine()
            engine2 = get_engine()
            assert engine1 is engine2


class TestGetAsyncSessionFactory:
    """Test get_async_session_factory function."""

    def setup_method(self):
        reset_engine()

    def teardown_method(self):
        reset_engine()

    def test_returns_session_factory(self):
        """get_async_session_factory should return an async_sessionmaker."""
        with patch("app.core.database.get_database_url") as mock_url:
            mock_url.return_value = "sqlite+aiosqlite:///:memory:"
            factory = get_async_session_factory()
            assert factory is not None

    def test_returns_same_factory(self):
        """get_async_session_factory should return the same instance."""
        with patch("app.core.database.get_database_url") as mock_url:
            mock_url.return_value = "sqlite+aiosqlite:///:memory:"
            f1 = get_async_session_factory()
            f2 = get_async_session_factory()
            assert f1 is f2


class TestGetDb:
    """Test get_db async generator."""

    def setup_method(self):
        reset_engine()

    def teardown_method(self):
        reset_engine()

    @pytest.mark.asyncio
    async def test_yields_session(self):
        """get_db should yield an AsyncSession."""
        from sqlalchemy.ext.asyncio import AsyncSession

        with patch("app.core.database.get_database_url") as mock_url:
            mock_url.return_value = "sqlite+aiosqlite:///:memory:"
            gen = get_db()
            session = await gen.__anext__()
            assert isinstance(session, AsyncSession)
            # Clean up
            try:
                await gen.__anext__()
            except StopAsyncIteration:
                pass


class TestInitDb:
    """Test init_db function."""

    def setup_method(self):
        reset_engine()

    def teardown_method(self):
        reset_engine()

    @pytest.mark.asyncio
    async def test_creates_tables(self):
        """init_db should create all tables without error."""
        with patch("app.core.database.get_database_url") as mock_url:
            mock_url.return_value = "sqlite+aiosqlite:///:memory:"
            await init_db()
            # If we get here without error, tables were created


class TestCloseDb:
    """Test close_db function."""

    def setup_method(self):
        reset_engine()

    def teardown_method(self):
        reset_engine()

    @pytest.mark.asyncio
    async def test_disposes_engine(self):
        """close_db should dispose the engine and reset state."""
        with patch("app.core.database.get_database_url") as mock_url:
            mock_url.return_value = "sqlite+aiosqlite:///:memory:"
            get_engine()  # Create the engine first
            await close_db()
            # After close, module-level _engine should be None
            assert db_module._engine is None
            assert db_module._async_session_factory is None

    @pytest.mark.asyncio
    async def test_noop_when_no_engine(self):
        """close_db should be safe to call when no engine exists."""
        await close_db()  # Should not raise


class TestResetEngine:
    """Test reset_engine function."""

    def test_clears_engine(self):
        """reset_engine should set _engine and _async_session_factory to None."""
        # Set some values
        db_module._engine = "fake"
        db_module._async_session_factory = "fake"
        reset_engine()
        assert db_module._engine is None
        assert db_module._async_session_factory is None


class TestRegisterQueryMetricsListeners:
    """Test _register_query_metrics_listeners."""

    def setup_method(self):
        # Reset the flag
        db_module._metrics_listeners_registered = False

    def teardown_method(self):
        db_module._metrics_listeners_registered = False

    def test_skips_in_test_mode(self, monkeypatch):
        """Should skip registration when TESTING=true."""
        monkeypatch.setenv("TESTING", "true")
        mock_engine = MagicMock()
        _register_query_metrics_listeners(mock_engine)
        assert db_module._metrics_listeners_registered is False

    def test_registers_when_forced(self, monkeypatch):
        """Should register listeners when force=True even in test mode."""
        monkeypatch.setenv("TESTING", "true")
        # Use a real sync engine so SQLAlchemy event registration works
        sync_engine = create_engine("sqlite:///:memory:")
        _register_query_metrics_listeners(sync_engine, force=True)
        assert db_module._metrics_listeners_registered is True

    def test_skips_if_already_registered(self, monkeypatch):
        """Should skip if already registered."""
        monkeypatch.delenv("TESTING", raising=False)
        db_module._metrics_listeners_registered = True
        mock_engine = MagicMock()
        # Should not call event.listens_for again
        _register_query_metrics_listeners(mock_engine)
        # Still True, didn't re-register
        assert db_module._metrics_listeners_registered is True

    def test_registers_in_non_test_mode(self, monkeypatch):
        """Should register in non-test mode."""
        monkeypatch.delenv("TESTING", raising=False)
        # Use a real sync engine so SQLAlchemy event registration works
        sync_engine = create_engine("sqlite:///:memory:")
        _register_query_metrics_listeners(sync_engine)
        assert db_module._metrics_listeners_registered is True


class TestEnableQueryMetricsForTesting:
    """Test enable_query_metrics_for_testing function."""

    def setup_method(self):
        reset_engine()
        db_module._metrics_listeners_registered = False

    def teardown_method(self):
        reset_engine()
        db_module._metrics_listeners_registered = False

    def test_enables_metrics_for_testing(self):
        """Should call _register_query_metrics_listeners with force=True."""
        with patch("app.core.database.get_database_url") as mock_url:
            mock_url.return_value = "sqlite+aiosqlite:///:memory:"
            # Create engine first
            engine = get_engine()
            enable_query_metrics_for_testing()
            assert db_module._metrics_listeners_registered is True


class TestQueryMetricsEventListeners:
    """Test the actual event listener callbacks that track query metrics."""

    def setup_method(self):
        db_module._metrics_listeners_registered = False

    def teardown_method(self):
        db_module._metrics_listeners_registered = False

    def test_select_query_records_metrics(self):
        """SELECT query should record duration with operation='select'."""
        from sqlalchemy import text

        engine = create_engine("sqlite:///:memory:")
        _register_query_metrics_listeners(engine, force=True)

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    def test_insert_query_records_metrics(self):
        """INSERT query should record duration with operation='insert'."""
        from sqlalchemy import text

        db_module._metrics_listeners_registered = False
        engine = create_engine("sqlite:///:memory:")
        _register_query_metrics_listeners(engine, force=True)

        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test_ins (id INTEGER PRIMARY KEY)"))
            conn.execute(text("INSERT INTO test_ins (id) VALUES (1)"))
            conn.commit()

    def test_update_query_records_metrics(self):
        """UPDATE query should record duration with operation='update'."""
        from sqlalchemy import text

        db_module._metrics_listeners_registered = False
        engine = create_engine("sqlite:///:memory:")
        _register_query_metrics_listeners(engine, force=True)

        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test_upd (id INTEGER, val TEXT)"))
            conn.execute(text("INSERT INTO test_upd (id, val) VALUES (1, 'a')"))
            conn.execute(text("UPDATE test_upd SET val = 'b' WHERE id = 1"))
            conn.commit()

    def test_delete_query_records_metrics(self):
        """DELETE query should record duration with operation='delete'."""
        from sqlalchemy import text

        db_module._metrics_listeners_registered = False
        engine = create_engine("sqlite:///:memory:")
        _register_query_metrics_listeners(engine, force=True)

        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test_del (id INTEGER)"))
            conn.execute(text("INSERT INTO test_del (id) VALUES (1)"))
            conn.execute(text("DELETE FROM test_del WHERE id = 1"))
            conn.commit()

    def test_missing_start_time_handled_gracefully(self):
        """After-execute should handle missing start_time (None path)."""
        from sqlalchemy import text, event

        db_module._metrics_listeners_registered = False
        engine = create_engine("sqlite:///:memory:")
        _register_query_metrics_listeners(engine, force=True)

        # Add a listener that clears _query_start_times after before_cursor
        # fires but before after_cursor fires, simulating the None path
        @event.listens_for(engine, "before_cursor_execute")
        def clear_start_times(conn, cursor, stmt, params, ctx, executemany):
            db_module._query_start_times.clear()

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
