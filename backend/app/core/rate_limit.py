"""Rate limiting configuration using slowapi."""

from fastapi import Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from app.core.errors import RateLimitError
from app.core.exception_handlers import app_error_handler


def get_client_ip(request: Request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For from trusted proxies.

    Only trusts X-Forwarded-For when the direct connection comes from a known
    proxy IP (configured via FORWARDED_ALLOW_IPS). When the connecting IP is
    not in the trusted list, returns the direct client IP instead.

    Production requirement: Set FORWARDED_ALLOW_IPS to your reverse proxy's
    IP range, or configure uvicorn's --forwarded-allow-ips flag.
    """
    from app.core.config import get_settings

    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for and request.client:
        settings = get_settings()
        trusted = {ip.strip() for ip in settings.forwarded_allow_ips.split(",")}
        if request.client.host in trusted:
            return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


limiter = Limiter(key_func=get_client_ip)


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Convert slowapi's RateLimitExceeded to the app error format."""
    return await app_error_handler(request, RateLimitError())
