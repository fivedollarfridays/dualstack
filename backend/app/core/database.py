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


def _register_query_metrics_listeners(engine, force: bool = False):
    """Register database query metrics listeners on the engine.

    Only registers if not in test mode (TESTING env var != 'true').
    This improves test performance by skipping metrics collection overhead.

    Args:
        engine: SQLAlchemy engine to register listeners on
        force: If True, register even in test mode (for metrics tests)
    """
    global _metrics_listeners_registered

    # Skip if already registered
    if _metrics_listeners_registered:
        return

    # Skip in test mode unless forced
    if not force and os.getenv("TESTING") == "true":
        return

    _metrics_listeners_registered = True

    @event.listens_for(engine, "before_cursor_execute")
    def receive_before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        """Store query start time before execution."""
        conn_id = id(conn)
        _query_start_times[conn_id] = time.time()

    @event.listens_for(engine, "after_cursor_execute")
    def receive_after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        """Calculate and record query duration after execution."""
        from app.core.metrics import db_query_duration_seconds

        conn_id = id(conn)
        start_time = _query_start_times.pop(conn_id, None)

        if start_time is not None:
            duration = time.time() - start_time

            # Determine operation type from SQL statement
            operation = "unknown"
            statement_upper = statement.strip().upper()
            if statement_upper.startswith("SELECT"):
                operation = "select"
            elif statement_upper.startswith("INSERT"):
                operation = "insert"
            elif statement_upper.startswith("UPDATE"):
                operation = "update"
            elif statement_upper.startswith("DELETE"):
                operation = "delete"

            db_query_duration_seconds.labels(operation=operation).observe(duration)


def enable_query_metrics_for_testing():
    """Enable query metrics even in test mode.

    Call this from tests that specifically test database metrics functionality.
    Must be called after get_engine() has been called.
    """
    engine = get_engine()
    _register_query_metrics_listeners(engine.sync_engine, force=True)


def get_database_url() -> str:
    """
    Get the database URL for SQLAlchemy.

    For Turso, we use libsql:// protocol in production.
    For testing, we use sqlite+aiosqlite:// with in-memory or file DB.
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
