"""Tests for the email service.

Validates email sending, async dispatch, error handling,
and provider SDK integration (all calls mocked).
"""

from unittest.mock import MagicMock, patch

import pytest

from app.core.email import EmailConfigError, EmailService


class TestEmailServiceInit:
    """EmailService initializes from config."""

    def test_creates_with_api_key(self) -> None:
        svc = EmailService(api_key="re_test_123", from_address="no-reply@example.com")
        assert svc.api_key == "re_test_123"
        assert svc.from_address == "no-reply@example.com"

    def test_default_from_name(self) -> None:
        svc = EmailService(api_key="re_test_123", from_address="no-reply@example.com")
        assert svc.from_name == "DualStack"

    def test_custom_from_name(self) -> None:
        svc = EmailService(
            api_key="re_test_123",
            from_address="no-reply@example.com",
            from_name="My App",
        )
        assert svc.from_name == "My App"


class TestEmailServiceSend:
    """EmailService.send() dispatches email via provider."""

    def _make_service(self) -> EmailService:
        return EmailService(api_key="re_test_123", from_address="no-reply@example.com")

    @patch("app.core.email.resend")
    def test_send_calls_provider(self, mock_resend: MagicMock) -> None:
        mock_resend.Emails.send.return_value = {"id": "msg_abc123"}
        svc = self._make_service()

        result = svc.send(
            to="user@example.com",
            subject="Hello",
            html="<p>Welcome</p>",
        )

        assert result == "msg_abc123"
        mock_resend.Emails.send.assert_called_once()
        call_args = mock_resend.Emails.send.call_args[0][0]
        assert call_args["to"] == ["user@example.com"]
        assert call_args["subject"] == "Hello"
        assert call_args["html"] == "<p>Welcome</p>"

    @patch("app.core.email.resend")
    def test_send_sets_from_address(self, mock_resend: MagicMock) -> None:
        mock_resend.Emails.send.return_value = {"id": "msg_1"}
        svc = self._make_service()
        svc.send(to="user@example.com", subject="Test", html="<p>body</p>")

        call_args = mock_resend.Emails.send.call_args[0][0]
        assert "no-reply@example.com" in call_args["from"]

    @patch("app.core.email.resend")
    def test_send_includes_from_name(self, mock_resend: MagicMock) -> None:
        mock_resend.Emails.send.return_value = {"id": "msg_1"}
        svc = EmailService(
            api_key="re_test_123",
            from_address="no-reply@example.com",
            from_name="My App",
        )
        svc.send(to="user@example.com", subject="Test", html="<p>body</p>")

        call_args = mock_resend.Emails.send.call_args[0][0]
        assert "My App" in call_args["from"]

    def test_send_raises_when_no_api_key(self) -> None:
        svc = EmailService(api_key="", from_address="no-reply@example.com")
        with pytest.raises(EmailConfigError, match="API key"):
            svc.send(to="user@example.com", subject="Test", html="<p>body</p>")

    @patch("app.core.email.resend")
    def test_send_accepts_list_of_recipients(self, mock_resend: MagicMock) -> None:
        mock_resend.Emails.send.return_value = {"id": "msg_1"}
        svc = self._make_service()
        svc.send(
            to=["a@example.com", "b@example.com"],
            subject="Test",
            html="<p>body</p>",
        )

        call_args = mock_resend.Emails.send.call_args[0][0]
        assert call_args["to"] == ["a@example.com", "b@example.com"]


class TestEmailServiceSendAsync:
    """EmailService.send_async() sends without blocking."""

    @pytest.mark.asyncio
    @patch("app.core.email.resend")
    async def test_send_async_returns_message_id(self, mock_resend: MagicMock) -> None:
        mock_resend.Emails.send.return_value = {"id": "msg_async_1"}
        svc = EmailService(api_key="re_test_123", from_address="no-reply@example.com")

        result = await svc.send_async(
            to="user@example.com",
            subject="Async Hello",
            html="<p>Async body</p>",
        )

        assert result == "msg_async_1"

    @pytest.mark.asyncio
    async def test_send_async_raises_when_no_api_key(self) -> None:
        svc = EmailService(api_key="", from_address="no-reply@example.com")
        with pytest.raises(EmailConfigError):
            await svc.send_async(
                to="user@example.com", subject="Test", html="<p>body</p>"
            )


class TestEmailServiceSendTemplate:
    """EmailService.send_template() renders then sends."""

    @patch("app.core.email.resend")
    def test_send_template_renders_and_sends(self, mock_resend: MagicMock) -> None:
        mock_resend.Emails.send.return_value = {"id": "msg_tpl_1"}
        svc = EmailService(api_key="re_test_123", from_address="no-reply@example.com")

        result = svc.send_template(
            to="user@example.com",
            template_name="welcome",
            template_data={"user_name": "Alice"},
        )

        assert result == "msg_tpl_1"
        call_args = mock_resend.Emails.send.call_args[0][0]
        assert "Alice" in call_args["html"]
        assert call_args["subject"]  # subject should be non-empty
