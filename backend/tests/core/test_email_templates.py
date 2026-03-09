"""Tests for email template rendering.

Validates template registry, rendering output, and error handling
for all transactional email templates.
"""

import pytest

from app.core.email_templates import TemplateNotFoundError, render_template


class TestTemplateRegistry:
    """Template registry returns subject + HTML for known templates."""

    def test_render_unknown_template_raises(self) -> None:
        with pytest.raises(TemplateNotFoundError, match="unknown_tpl"):
            render_template("unknown_tpl", {})

    def test_render_returns_subject_and_html(self) -> None:
        result = render_template("welcome", {"user_name": "Alice"})
        assert "subject" in result
        assert "html" in result
        assert len(result["subject"]) > 0
        assert len(result["html"]) > 0


class TestWelcomeTemplate:
    """Welcome email template."""

    def test_includes_user_name(self) -> None:
        result = render_template("welcome", {"user_name": "Bob"})
        assert "Bob" in result["html"]

    def test_has_subject(self) -> None:
        result = render_template("welcome", {"user_name": "Bob"})
        assert "welcome" in result["subject"].lower() or "Welcome" in result["subject"]

    def test_missing_user_name_uses_fallback(self) -> None:
        result = render_template("welcome", {})
        assert result["html"]  # should not crash


class TestBillingReceiptTemplate:
    """Billing receipt email template."""

    def test_includes_amount(self) -> None:
        result = render_template(
            "billing_receipt",
            {"amount": "$29.00", "plan": "Pro", "date": "2026-03-09"},
        )
        assert "$29.00" in result["html"]

    def test_includes_plan_name(self) -> None:
        result = render_template(
            "billing_receipt",
            {"amount": "$29.00", "plan": "Pro", "date": "2026-03-09"},
        )
        assert "Pro" in result["html"]

    def test_has_subject(self) -> None:
        result = render_template(
            "billing_receipt",
            {"amount": "$29.00", "plan": "Pro", "date": "2026-03-09"},
        )
        assert result["subject"]


class TestNotificationTemplate:
    """Generic notification email template."""

    def test_includes_title(self) -> None:
        result = render_template(
            "notification",
            {"title": "Alert fired", "message": "CPU usage is high"},
        )
        assert "Alert fired" in result["html"]

    def test_includes_message(self) -> None:
        result = render_template(
            "notification",
            {"title": "Alert", "message": "Something happened"},
        )
        assert "Something happened" in result["html"]

    def test_has_subject_from_title(self) -> None:
        result = render_template(
            "notification",
            {"title": "Important Update", "message": "Details here"},
        )
        assert "Important Update" in result["subject"]

    def test_missing_fields_uses_fallback(self) -> None:
        result = render_template("notification", {})
        assert result["html"]
        assert result["subject"]
