"""
Database Configuration

SQLAlchemy 2.0 async setup for Turso/SQLite.
Provides session management and base model class.
"""

import os
import time

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# Query duration tracking with SQLAlchemy event listeners
# Only enabled in non-test environments to avoid test overhead
_query_start_times = {}
_metrics_listeners_registered = False


_OP_TYPE_MAP = {"SELECT": "select", "INSERT": "insert", "UPDATE": "update", "DELETE": "delete"}


def _get_operation_type(statement: str) -> str:
    """Extract the SQL operation type from a statement."""
    stripped = statement.strip()
    keyword = stripped.split(None, 1)[0].upper() if stripped else ""
    return _OP_TYPE_MAP.get(keyword, "unknown")


def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Store query start time before execution."""
    _query_start_times[id(conn)] = time.time()


def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Calculate and record query duration after execution."""
    from app.core.metrics import db_query_duration_seconds

    start_time = _query_start_times.pop(id(conn), None)
    if start_time is not None:
        duration = time.time() - start_time
        db_query_duration_seconds.labels(operation=_get_operation_type(statement)).observe(duration)


def _register_query_metrics_listeners(engine, force: bool = False):
    """Register database query metrics listeners on the engine.

    Only registers if not in test mode (TESTING env var != 'true').
    """
    global _metrics_listeners_registered

    if _metrics_listeners_registered:
        return
    if not force and os.getenv("TESTING") == "true":
        return

    _metrics_listeners_registered = True
    event.listen(engine, "before_cursor_execute", _before_cursor_execute)
    event.listen(engine, "after_cursor_execute", _after_cursor_execute)


def enable_query_metrics_for_testing():
    """Enable query metrics even in test mode.

    Call this from tests that specifically test database metrics functionality.
    Must be called after get_engine() has been called.
    """
    engine = get_engine()
    _register_query_metrics_listeners(engine.sync_engine, force=True)


def get_database_url() -> str:
    """Get the database URL for SQLAlchemy.

    Currently falls back to local SQLite for libsql:// URLs because
    SQLAlchemy does not natively support the libsql:// protocol.
    Production Turso support requires an async-compatible driver such
    as ``libsql-client`` or a dedicated SQLAlchemy dialect (e.g.
    ``sqlalchemy-libsql``). This is a known limitation of the starter
    kit -- Turso URLs are detected but served by a local SQLite file
    (``dualstack.db``) until a compatible driver is integrated.

    For testing, an in-memory SQLite database is used by default.
    """
    settings = get_settings()

    if settings.turso_database_url:
        # Turso uses libsql:// but SQLAlchemy needs sqlite+aiosqlite://
        # For local dev/test, use SQLite directly
        url = settings.turso_database_url
        if url.startswith("libsql://"):
            # Convert to HTTP endpoint for turso-client
            # For now, use local SQLite for development
            return "sqlite+aiosqlite:///./dualstack.db"
        return url

    # Default to in-memory SQLite for testing
    return "sqlite+aiosqlite:///:memory:"


# Engine creation is deferred to allow testing with different URLs
_engine = None
_async_session_factory = None


def get_engine():
    """Get or create the async engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            get_database_url(),
            echo=False,  # Disabled for Windows compatibility with emoji content
        )
        # Register metrics listeners (skipped in test mode)
        _register_query_metrics_listeners(_engine.sync_engine)
    return _engine


def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get the async session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_factory


async def get_db() -> AsyncSession:
    """
    Dependency for FastAPI routes to get a database session.

    Yields an AsyncSession that is automatically closed after use.
    """
    async_session = get_async_session_factory()
    async with async_session() as session:
        yield session


async def init_db() -> None:
    """Initialize the database by creating all tables."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close the database engine."""
    global _engine, _async_session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None


def reset_engine() -> None:
    """Reset engine for testing purposes."""
    global _engine, _async_session_factory
    _engine = None
    _async_session_factory = None
