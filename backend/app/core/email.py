"""Email service for transactional emails via Resend."""

import asyncio

import resend

from app.core.email_templates import render_template


class EmailConfigError(Exception):
    """Raised when email provider is not configured."""


class EmailService:
    """Sends transactional emails via Resend SDK."""

    def __init__(
        self,
        api_key: str,
        from_address: str,
        from_name: str = "DualStack",
    ) -> None:
        self.api_key = api_key
        self.from_address = from_address
        self.from_name = from_name
        resend.api_key = api_key

    def _ensure_configured(self) -> None:
        if not self.api_key:
            raise EmailConfigError("Email API key is not configured")

    def send(
        self,
        to: str | list[str],
        subject: str,
        html: str,
    ) -> str:
        """Send an email. Returns the message ID."""
        self._ensure_configured()

        recipients = to if isinstance(to, list) else [to]
        result = resend.Emails.send(
            {
                "from": f"{self.from_name} <{self.from_address}>",
                "to": recipients,
                "subject": subject,
                "html": html,
            }
        )
        return result["id"]

    async def send_async(
        self,
        to: str | list[str],
        subject: str,
        html: str,
    ) -> str:
        """Send an email without blocking the event loop."""
        return await asyncio.to_thread(self.send, to, subject, html)

    def send_template(
        self,
        to: str | list[str],
        template_name: str,
        template_data: dict | None = None,
    ) -> str:
        """Render a template and send the email."""
        rendered = render_template(template_name, template_data or {})
        return self.send(to=to, subject=rendered["subject"], html=rendered["html"])

    async def send_template_async(
        self,
        to: str | list[str],
        template_name: str,
        template_data: dict | None = None,
    ) -> str:
        """Render a template and send the email without blocking the event loop."""
        rendered = render_template(template_name, template_data or {})
        return await self.send_async(
            to=to, subject=rendered["subject"], html=rendered["html"]
        )
