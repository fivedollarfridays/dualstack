"""URL validation utilities for redirect safety."""

from urllib.parse import urlparse

from app.core.config import get_settings


def get_allowed_origins() -> list[str]:
    """Get allowed redirect origins from CORS config."""
    return get_settings().get_cors_origins()


def validate_redirect_url(url: str) -> str:
    """Validate a redirect URL is on an allowed origin.

    Raises ValueError if the URL's origin is not in the allowed list.
    """
    allowed = get_allowed_origins()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http and https URLs are allowed")
    if not parsed.netloc:
        raise ValueError("URL must have a valid host")
    if parsed.username or parsed.password:
        raise ValueError("URLs with embedded credentials are not allowed")
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin not in allowed:
        raise ValueError("URL origin is not allowed")
    return url
