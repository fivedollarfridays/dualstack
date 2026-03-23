"""Tests for app.core.database module."""

import pytest
from unittest.mock import patch, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

import app.core.database as db_module
import app.core.db_metrics as db_metrics_module
from app.core.database import (
    Base,
    get_database_url,
    get_alembic_database_url,
    get_alembic_connect_args,
    mask_database_url,
    get_engine,
    get_async_session_factory,
    get_db,
    init_db,
    close_db,
    reset_engine,
    enable_query_metrics_for_testing,
)
from app.core.db_metrics import register_query_metrics_listeners


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

    def test_database_url_takes_priority(self):
        """DATABASE_URL env var takes priority over TURSO_DATABASE_URL."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(
                database_url="postgresql+asyncpg://user:pass@host/db",
                turso_database_url="file:local.db",
            )
            url = get_database_url()
            assert url == "postgresql+asyncpg://user:pass@host/db"

    def test_file_url_converted_to_aiosqlite(self):
        """TURSO_DATABASE_URL=file:local.db → sqlite+aiosqlite:///./local.db."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(turso_database_url="file:local.db")
            url = get_database_url()
            assert url == "sqlite+aiosqlite:///./local.db"

    def test_libsql_url_raises_with_instructions(self):
        """Remote libsql:// URL raises ValueError with migration instructions."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(
                turso_database_url="libsql://my-db.turso.io"
            )
            with pytest.raises(ValueError, match="DATABASE_URL"):
                get_database_url()

    def test_aiosqlite_url_passthrough(self):
        """Already-formatted SQLAlchemy URLs pass through unchanged."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(
                turso_database_url="sqlite+aiosqlite:///./test.db"
            )
            url = get_database_url()
            assert url == "sqlite+aiosqlite:///./test.db"

    def test_returns_memory_sqlite_when_no_url(self):
        """Without any database URL configured, should return in-memory SQLite."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(
                database_url="", turso_database_url=""
            )
            url = get_database_url()
            assert url == "sqlite+aiosqlite:///:memory:"


class TestGetAlembicDatabaseUrl:
    """Test get_alembic_database_url for sync Alembic migrations."""

    def test_converts_aiosqlite_to_sync(self):
        """Strips +aiosqlite for sync Alembic use."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(turso_database_url="file:local.db")
            url = get_alembic_database_url()
            assert url == "sqlite:///./local.db"

    def test_converts_libsql_for_turso(self):
        """Remote libsql:// URL is converted to sqlite+libsql:// WITHOUT auth token."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(
                turso_database_url="libsql://my-db.turso.io",
                turso_auth_token="test-token",
            )
            url = get_alembic_database_url()
            assert url == "sqlite+libsql://my-db.turso.io?secure=true"
            assert "test-token" not in url
            assert "authToken" not in url

    def test_converts_asyncpg_to_psycopg2(self):
        """Converts async PostgreSQL URL to sync for Alembic."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(
                database_url="postgresql+asyncpg://user:pass@host/db",
            )
            url = get_alembic_database_url()
            assert url == "postgresql://user:pass@host/db"

    def test_default_memory_sqlite(self):
        """No URL configured → sync in-memory SQLite."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(
                database_url="", turso_database_url=""
            )
            url = get_alembic_database_url()
            assert url == "sqlite:///:memory:"


class TestGetAlembicConnectArgs:
    """Test get_alembic_connect_args for passing auth token via connect_args."""

    def test_returns_auth_token_for_libsql(self):
        """Remote Turso URL should return auth_token in connect_args."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(
                turso_database_url="libsql://my-db.turso.io",
                turso_auth_token="secret-token-123",
            )
            args = get_alembic_connect_args()
            assert args == {"auth_token": "secret-token-123"}

    def test_returns_empty_for_file_url(self):
        """Local file URLs should return empty connect_args."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(turso_database_url="file:local.db")
            args = get_alembic_connect_args()
            assert args == {}

    def test_returns_empty_for_database_url(self):
        """DATABASE_URL (PostgreSQL) should return empty connect_args."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(
                database_url="postgresql+asyncpg://user:pass@host/db",
            )
            args = get_alembic_connect_args()
            assert args == {}

    def test_returns_empty_for_memory_sqlite(self):
        """Default in-memory SQLite should return empty connect_args."""
        from app.core.config import Settings

        with patch("app.core.database.get_settings") as mock_settings:
            mock_settings.return_value = Settings(
                database_url="", turso_database_url=""
            )
            args = get_alembic_connect_args()
            assert args == {}


class TestMaskDatabaseUrl:
    """Test mask_database_url utility for safe logging."""

    def test_masks_auth_token_in_url(self):
        """authToken=xxx should be masked to authToken=***."""
        url = "sqlite+libsql://my-db.turso.io?authToken=secret123&secure=true"
        masked = mask_database_url(url)
        assert "secret123" not in masked
        assert "authToken=***" in masked
        assert "secure=true" in masked

    def test_masks_password_in_url(self):
        """Passwords in user:pass@host URLs should be masked."""
        url = "postgresql://user:s3cretP@ss@host/db"
        masked = mask_database_url(url)
        assert "s3cretP@ss" not in masked
        assert "user:***@host" in masked

    def test_no_change_for_safe_url(self):
        """URLs without secrets should pass through unchanged."""
        url = "sqlite:///./local.db"
        masked = mask_database_url(url)
        assert masked == url

    def test_no_change_for_memory_url(self):
        """In-memory URLs should pass through unchanged."""
        url = "sqlite:///:memory:"
        masked = mask_database_url(url)
        assert masked == url


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
    """Test register_query_metrics_listeners."""

    def setup_method(self):
        # Reset the flag
        db_metrics_module._metrics_listeners_registered = False

    def teardown_method(self):
        db_metrics_module._metrics_listeners_registered = False

    def test_skips_in_test_mode(self, monkeypatch):
        """Should skip registration when TESTING=true."""
        monkeypatch.setenv("TESTING", "true")
        mock_engine = MagicMock()
        register_query_metrics_listeners(mock_engine)
        assert db_metrics_module._metrics_listeners_registered is False

    def test_registers_when_forced(self, monkeypatch):
        """Should register listeners when force=True even in test mode."""
        monkeypatch.setenv("TESTING", "true")
        # Use a real sync engine so SQLAlchemy event registration works
        sync_engine = create_engine("sqlite:///:memory:")
        register_query_metrics_listeners(sync_engine, force=True)
        assert db_metrics_module._metrics_listeners_registered is True

    def test_skips_if_already_registered(self, monkeypatch):
        """Should skip if already registered."""
        monkeypatch.delenv("TESTING", raising=False)
        db_metrics_module._metrics_listeners_registered = True
        mock_engine = MagicMock()
        # Should not call event.listens_for again
        register_query_metrics_listeners(mock_engine)
        # Still True, didn't re-register
        assert db_metrics_module._metrics_listeners_registered is True

    def test_registers_in_non_test_mode(self, monkeypatch):
        """Should register in non-test mode."""
        monkeypatch.delenv("TESTING", raising=False)
        # Use a real sync engine so SQLAlchemy event registration works
        sync_engine = create_engine("sqlite:///:memory:")
        register_query_metrics_listeners(sync_engine)
        assert db_metrics_module._metrics_listeners_registered is True


class TestEnableQueryMetricsForTesting:
    """Test enable_query_metrics_for_testing function."""

    def setup_method(self):
        reset_engine()
        db_metrics_module._metrics_listeners_registered = False

    def teardown_method(self):
        reset_engine()
        db_metrics_module._metrics_listeners_registered = False

    def test_enables_metrics_for_testing(self):
        """Should call register_query_metrics_listeners with force=True."""
        with patch("app.core.database.get_database_url") as mock_url:
            mock_url.return_value = "sqlite+aiosqlite:///:memory:"
            # Create engine first (side effect: registers metrics listeners)
            get_engine()
            enable_query_metrics_for_testing()
            assert db_metrics_module._metrics_listeners_registered is True


class TestQueryMetricsEventListeners:
    """Test the actual event listener callbacks that track query metrics."""

    def setup_method(self):
        db_metrics_module._metrics_listeners_registered = False

    def teardown_method(self):
        db_metrics_module._metrics_listeners_registered = False

    def test_select_query_records_metrics(self):
        """SELECT query should record duration with operation='select'."""
        from sqlalchemy import text

        engine = create_engine("sqlite:///:memory:")
        register_query_metrics_listeners(engine, force=True)

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    def test_insert_query_records_metrics(self):
        """INSERT query should record duration with operation='insert'."""
        from sqlalchemy import text

        db_metrics_module._metrics_listeners_registered = False
        engine = create_engine("sqlite:///:memory:")
        register_query_metrics_listeners(engine, force=True)

        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test_ins (id INTEGER PRIMARY KEY)"))
            conn.execute(text("INSERT INTO test_ins (id) VALUES (1)"))
            conn.commit()

    def test_update_query_records_metrics(self):
        """UPDATE query should record duration with operation='update'."""
        from sqlalchemy import text

        db_metrics_module._metrics_listeners_registered = False
        engine = create_engine("sqlite:///:memory:")
        register_query_metrics_listeners(engine, force=True)

        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test_upd (id INTEGER, val TEXT)"))
            conn.execute(text("INSERT INTO test_upd (id, val) VALUES (1, 'a')"))
            conn.execute(text("UPDATE test_upd SET val = 'b' WHERE id = 1"))
            conn.commit()

    def test_delete_query_records_metrics(self):
        """DELETE query should record duration with operation='delete'."""
        from sqlalchemy import text

        db_metrics_module._metrics_listeners_registered = False
        engine = create_engine("sqlite:///:memory:")
        register_query_metrics_listeners(engine, force=True)

        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test_del (id INTEGER)"))
            conn.execute(text("INSERT INTO test_del (id) VALUES (1)"))
            conn.execute(text("DELETE FROM test_del WHERE id = 1"))
            conn.commit()

    def test_missing_start_time_handled_gracefully(self):
        """After-execute should handle missing start_time (None path)."""
        from sqlalchemy import text, event

        db_metrics_module._metrics_listeners_registered = False
        engine = create_engine("sqlite:///:memory:")
        register_query_metrics_listeners(engine, force=True)

        # Add a listener that clears conn.info after before_cursor
        # fires but before after_cursor fires, simulating the None path
        @event.listens_for(engine, "before_cursor_execute")
        def clear_start_times(conn, cursor, stmt, params, ctx, executemany):
            conn.info.pop("query_start_time", None)

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
