"""Database query metrics via SQLAlchemy event listeners."""

import os
import time

from sqlalchemy import event

# Cached reference — resolved on first query, avoids per-query import overhead
_db_query_duration_seconds = None

_metrics_listeners_registered = False

_OP_TYPE_MAP = {
    "SELECT": "select",
    "INSERT": "insert",
    "UPDATE": "update",
    "DELETE": "delete",
}


def _get_operation_type(statement: str) -> str:
    """Extract the SQL operation type from a statement."""
    stripped = statement.strip()
    keyword = stripped.split(None, 1)[0].upper() if stripped else ""
    return _OP_TYPE_MAP.get(keyword, "unknown")


def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany) -> None:
    """Store query start time before execution."""
    conn.info["query_start_time"] = time.time()


def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany) -> None:
    """Calculate and record query duration after execution."""
    global _db_query_duration_seconds
    if _db_query_duration_seconds is None:
        from app.core.metrics import db_query_duration_seconds

        _db_query_duration_seconds = db_query_duration_seconds

    start_time = conn.info.pop("query_start_time", None)
    if start_time is not None:
        duration = time.time() - start_time
        _db_query_duration_seconds.labels(
            operation=_get_operation_type(statement)
        ).observe(duration)


def register_query_metrics_listeners(engine, force: bool = False) -> None:
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


def reset_metrics_listeners() -> None:
    """Reset the registration flag so listeners can be re-registered on a new engine."""
    global _metrics_listeners_registered
    _metrics_listeners_registered = False
