"""Welcome email template."""

from html import escape


def render(data: dict) -> dict[str, str]:
    user_name = escape(data.get("user_name", "there"))
    return {
        "subject": f"Welcome to DualStack, {user_name}!",
        "html": (
            f"<h1>Welcome, {user_name}!</h1>"
            "<p>Thanks for signing up for DualStack. "
            "You're all set to start building.</p>"
            "<p>If you have any questions, just reply to this email.</p>"
        ),
    }
