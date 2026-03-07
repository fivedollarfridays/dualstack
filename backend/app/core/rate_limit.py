"""Rate limiting configuration using slowapi."""

from fastapi import Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from app.core.errors import RateLimitError
from app.core.exception_handlers import app_error_handler


def get_client_ip(request: Request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For from reverse proxies.

    Trusts the leftmost IP in X-Forwarded-For. This is safe when deployed behind
    a reverse proxy (e.g. Render) that overwrites the header. See entrypoint.sh
    for --forwarded-allow-ips configuration.
    """
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


limiter = Limiter(key_func=get_client_ip)


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Convert slowapi's RateLimitExceeded to the app error format."""
    return await app_error_handler(request, RateLimitError())
