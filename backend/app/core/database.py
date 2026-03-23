"""
Database Configuration

SQLAlchemy 2.0 async setup with environment-specific drivers.
Provides session management and base model class.
"""

import re

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings
from app.core.db_metrics import (
    register_query_metrics_listeners,
    reset_metrics_listeners,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


def escape_like(value: str) -> str:
    """Escape SQL LIKE wildcards for safe use in ILIKE/LIKE patterns."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def enable_query_metrics_for_testing() -> None:
    """Enable query metrics even in test mode.

    Call this from tests that specifically test database metrics functionality.
    Must be called after get_engine() has been called.
    """
    engine = get_engine()
    register_query_metrics_listeners(engine.sync_engine, force=True)


def get_database_url() -> str:
    """Get the async database URL for SQLAlchemy.

    Resolution order:
      1. DATABASE_URL (production — PostgreSQL via asyncpg, etc.)
      2. TURSO_DATABASE_URL with ``file:`` prefix (local dev — SQLite via aiosqlite)
      3. TURSO_DATABASE_URL with ``libsql://`` prefix → raises ValueError
         (no async libsql driver; set DATABASE_URL for production)
      4. TURSO_DATABASE_URL with SQLAlchemy URL → pass through
      5. Default: in-memory SQLite for testing
    """
    settings = get_settings()

    if settings.database_url:
        return settings.database_url

    if settings.turso_database_url:
        url = settings.turso_database_url
        if url.startswith("file:"):
            path = url.removeprefix("file:")
            return f"sqlite+aiosqlite:///./{path}"
        if url.startswith("libsql://"):
            raise ValueError(
                "Remote Turso URLs (libsql://) require a sync driver and cannot "
                "be used with the async SQLAlchemy engine. Set DATABASE_URL to an "
                "async-compatible URL (e.g. postgresql+asyncpg://user:pass@host/db) "
                "for production, or use TURSO_DATABASE_URL=file:local.db for local "
                "development."
            )
        return url

    return "sqlite+aiosqlite:///:memory:"


def get_alembic_database_url() -> str:
    """Get a sync database URL for Alembic migrations.

    Converts async URLs to sync equivalents, and converts remote
    Turso ``libsql://`` URLs to the ``sqlite+libsql://`` dialect
    provided by ``sqlalchemy-libsql``.
    """
    settings = get_settings()

    if settings.database_url:
        url = settings.database_url
        return url.replace("+asyncpg", "").replace("+aiosqlite", "")

    if settings.turso_database_url:
        url = settings.turso_database_url
        if url.startswith("file:"):
            path = url.removeprefix("file:")
            return f"sqlite:///./{path}"
        if url.startswith("libsql://"):
            host = url.removeprefix("libsql://")
            # Auth token is passed via connect_args (see get_alembic_connect_args),
            # NOT in the URL, to prevent token leaks in logs.
            return f"sqlite+libsql://{host}?secure=true"
        return url.replace("+aiosqlite", "")

    return "sqlite:///:memory:"


def get_alembic_connect_args() -> dict:
    """Get connect_args for Alembic engine creation.

    Returns auth_token separately from the URL so it never appears
    in log output from SQLAlchemy or Alembic.
    """
    settings = get_settings()

    if not settings.database_url and settings.turso_database_url:
        if settings.turso_database_url.startswith("libsql://"):
            return {"auth_token": settings.turso_auth_token}

    return {}


def mask_database_url(url: str) -> str:
    """Mask secrets in a database URL for safe logging.

    Replaces authToken query parameter values and user:password
    credentials with '***'.
    """
    # Mask authToken=xxx query parameter
    masked = re.sub(r"authToken=[^&]*", "authToken=***", url)
    # Mask user:password@host patterns (use .+ greedy to match last @)
    masked = re.sub(r"://([^:]+):.+@", r"://\1:***@", masked)
    return masked


# Engine creation is deferred to allow testing with different URLs
_engine = None
_async_session_factory = None


def get_engine() -> AsyncEngine:
    """Get or create the async engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            get_database_url(),
            echo=False,  # Disabled for Windows compatibility with emoji content
        )
        # Register metrics listeners (skipped in test mode)
        register_query_metrics_listeners(_engine.sync_engine)
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
        reset_metrics_listeners()


def reset_engine() -> None:
    """Reset engine for testing purposes."""
    global _engine, _async_session_factory
    _engine = None
    _async_session_factory = None
    reset_metrics_listeners()
