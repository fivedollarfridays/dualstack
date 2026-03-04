"""Shared test helpers for the DualStack backend test suite."""

from unittest.mock import MagicMock


def mock_settings_with_cors(cors_origins: str) -> MagicMock:
    """Create a mock Settings with given cors_origins.

    Args:
        cors_origins: Comma-separated origins string (e.g., "http://localhost:3000").
    """
    settings = MagicMock()
    settings.get_cors_origins.return_value = [
        o.strip() for o in cors_origins.split(",") if o.strip()
    ]
    return settings
