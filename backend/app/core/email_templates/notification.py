"""Generic notification email template."""

from html import escape


def render(data: dict) -> dict[str, str]:
    title = escape(data.get("title", "Notification"))
    message = escape(data.get("message", "You have a new notification."))
    return {
        "subject": title,
        "html": (
            f"<h1>{title}</h1>"
            f"<p>{message}</p>"
        ),
    }
