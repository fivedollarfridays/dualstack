"""Tests for audit logging (SEC-013)."""

from unittest.mock import AsyncMock, patch


from app.core.audit import log_audit_event, persist_audit_event


class TestLogAuditEvent:
    """Test structured audit log emission."""

    def test_emits_structured_log(self):
        """log_audit_event should emit a structured log with required fields."""
        with patch("app.core.audit.logger") as mock_logger:
            log_audit_event(
                user_id="user-1",
                action="create",
                resource_type="item",
                resource_id="item-abc",
            )
            mock_logger.info.assert_called_once()
            call_kwargs = mock_logger.info.call_args
            # Check the message
            assert "audit" in call_kwargs[0][0].lower()

    def test_includes_required_fields(self):
        """Audit event should include user_id, action, resource_type, resource_id."""
        with patch("app.core.audit.logger") as mock_logger:
            log_audit_event(
                user_id="user-42",
                action="delete",
                resource_type="item",
                resource_id="item-xyz",
            )
            kwargs = mock_logger.info.call_args[1]
            assert kwargs["user_id"] == "user-42"
            assert kwargs["action"] == "delete"
            assert kwargs["resource_type"] == "item"
            assert kwargs["resource_id"] == "item-xyz"

    def test_does_not_include_manual_timestamp(self):
        """Audit event should not include a manual timestamp (structlog TimeStamper handles it)."""
        with patch("app.core.audit.logger") as mock_logger:
            log_audit_event(
                user_id="user-1",
                action="update",
                resource_type="item",
                resource_id="item-123",
            )
            kwargs = mock_logger.info.call_args[1]
            assert "timestamp" not in kwargs

    def test_accepts_outcome_parameter(self):
        """log_audit_event should accept optional outcome parameter."""
        with patch("app.core.audit.logger") as mock_logger:
            log_audit_event(
                user_id="user-1",
                action="auth.login",
                resource_type="session",
                resource_id="unknown",
                outcome="failure",
            )
            kwargs = mock_logger.info.call_args[1]
            assert kwargs["outcome"] == "failure"

    def test_accepts_detail_parameter(self):
        """log_audit_event should accept optional detail parameter."""
        with patch("app.core.audit.logger") as mock_logger:
            log_audit_event(
                user_id="user-1",
                action="auth.login",
                resource_type="session",
                resource_id="unknown",
                detail="Invalid JWT",
            )
            kwargs = mock_logger.info.call_args[1]
            assert kwargs["detail"] == "Invalid JWT"

    def test_defaults_outcome_to_success(self):
        """outcome should default to 'success' when not provided."""
        with patch("app.core.audit.logger") as mock_logger:
            log_audit_event(
                user_id="user-1",
                action="create",
                resource_type="item",
                resource_id="item-1",
            )
            kwargs = mock_logger.info.call_args[1]
            assert kwargs["outcome"] == "success"

    def test_omits_detail_when_empty(self):
        """detail should not appear in log kwargs when not provided."""
        with patch("app.core.audit.logger") as mock_logger:
            log_audit_event(
                user_id="user-1",
                action="create",
                resource_type="item",
                resource_id="item-1",
            )
            kwargs = mock_logger.info.call_args[1]
            assert "detail" not in kwargs


class TestPersistAuditEvent:
    """Test database-persisted audit events."""

    async def test_persists_audit_entry_to_db(self):
        db = AsyncMock()
        await persist_audit_event(
            db,
            user_id="user-1",
            action="create",
            resource_type="item",
            resource_id="item-1",
        )
        db.add.assert_called_once()
        db.flush.assert_awaited_once()

    async def test_also_emits_structured_log(self):
        db = AsyncMock()
        with patch("app.core.audit.logger") as mock_logger:
            await persist_audit_event(
                db,
                user_id="user-1",
                action="create",
                resource_type="item",
                resource_id="item-1",
            )
            mock_logger.info.assert_called_once()
