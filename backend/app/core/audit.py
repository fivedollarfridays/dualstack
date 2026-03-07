"""Structured audit logging for write operations."""

from app.core.logging import get_logger

logger = get_logger("audit")


def log_audit_event(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    outcome: str = "success",
    detail: str = "",
) -> None:
    """Emit a structured audit log event."""
    kwargs: dict[str, str] = {
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "outcome": outcome,
    }
    if detail:
        kwargs["detail"] = detail
    logger.info("audit_event", **kwargs)
