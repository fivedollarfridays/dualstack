"""PII scrubbing for Stripe webhook event data.

Strips personally identifiable information (email, name, address, phone)
from webhook payloads before they are logged or persisted to audit trails.
"""

import copy
from typing import Any

_REDACTED = "[REDACTED]"

# Top-level keys to remove entirely
_TOP_LEVEL_REMOVE = frozenset({"customer_email", "receipt_email"})

# Keys within nested dicts whose values should be redacted
_PII_KEYS = frozenset({"name", "email", "phone", "address"})

# Top-level dict keys that may contain PII sub-fields
_PII_CONTAINERS = ("customer_details", "billing_details", "shipping")


def _redact_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Redact PII keys within a single dict."""
    result = {}
    for key, value in d.items():
        if key in _PII_KEYS:
            result[key] = _REDACTED
        else:
            result[key] = value
    return result


def scrub_pii(event_data: dict[str, Any]) -> dict[str, Any]:
    """Remove PII fields from Stripe webhook event data before logging.

    Preserves business-critical identifiers (customer ID, subscription ID,
    charge ID, status) while stripping personal information.

    Args:
        event_data: The ``data.object`` dict from a Stripe webhook event.

    Returns:
        A deep copy with PII fields redacted or removed.
    """
    scrubbed = copy.deepcopy(event_data)

    # Remove top-level PII keys
    for key in _TOP_LEVEL_REMOVE:
        scrubbed.pop(key, None)

    # Redact PII in known container dicts
    for container_key in _PII_CONTAINERS:
        if container_key in scrubbed and isinstance(scrubbed[container_key], dict):
            scrubbed[container_key] = _redact_dict(scrubbed[container_key])

    # Redact PII in nested charges
    charges = scrubbed.get("charges")
    if isinstance(charges, dict):
        for charge in charges.get("data", []):
            if isinstance(charge, dict):
                for container_key in _PII_CONTAINERS:
                    if container_key in charge and isinstance(
                        charge[container_key], dict
                    ):
                        charge[container_key] = _redact_dict(charge[container_key])

    return scrubbed
