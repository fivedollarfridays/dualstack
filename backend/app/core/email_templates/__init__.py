"""Email template registry and renderer."""

from typing import Callable

from app.core.email_templates.welcome import render as _render_welcome
from app.core.email_templates.billing_receipt import render as _render_billing_receipt
from app.core.email_templates.notification import render as _render_notification


class TemplateNotFoundError(Exception):
    """Raised when a requested email template does not exist."""


_REGISTRY: dict[str, Callable] = {
    "welcome": _render_welcome,
    "billing_receipt": _render_billing_receipt,
    "notification": _render_notification,
}


def render_template(name: str, data: dict) -> dict[str, str]:
    """Render a named template with the given data.

    Returns:
        dict with "subject" and "html" keys.

    Raises:
        TemplateNotFoundError: if template name is not registered.
    """
    renderer = _REGISTRY.get(name)
    if renderer is None:
        raise TemplateNotFoundError(f"Email template not found: {name}")
    return renderer(data)
