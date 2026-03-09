"""Billing receipt email template."""

from html import escape


def render(data: dict) -> dict[str, str]:
    amount = escape(data.get("amount", "$0.00"))
    plan = escape(data.get("plan", "Unknown"))
    date = escape(data.get("date", "N/A"))
    return {
        "subject": f"Payment receipt — {plan} plan",
        "html": (
            "<h1>Payment Receipt</h1>"
            f"<p>Thank you for your payment of <strong>{amount}</strong> "
            f"for the <strong>{plan}</strong> plan.</p>"
            f"<p>Date: {date}</p>"
            "<p>If you have questions about this charge, "
            "please contact support.</p>"
        ),
    }
