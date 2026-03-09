"""Structured audit logging for write operations."""

from sqlalchemy.ext.asyncio import AsyncSession

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
    """Emit a structured audit log event (log-only, no DB)."""
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


async def persist_audit_event(
    db: AsyncSession,
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    outcome: str = "success",
    detail: str = "",
) -> None:
    """Write an audit event to the database and emit a structured log."""
    from app.admin.models import AuditLog

    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
        detail=detail,
    )
    db.add(entry)
    await db.flush()

    log_audit_event(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
        detail=detail,
    )
