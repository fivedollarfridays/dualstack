"""Rate limiting configuration using slowapi."""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from app.core.errors import RateLimitError
from app.core.exception_handlers import app_error_handler


_trusted_ips: set[str] | None = None


def _get_trusted_ips() -> set[str]:
    """Parse and cache the trusted proxy IP set."""
    global _trusted_ips
    if _trusted_ips is None:
        from app.core.config import get_settings

        settings = get_settings()
        _trusted_ips = {ip.strip() for ip in settings.forwarded_allow_ips.split(",")}
    return _trusted_ips


def resolve_client_ip(
    direct_ip: str | None, headers: dict[str, str] | None = None
) -> str:
    """Resolve client IP using proxy-aware logic.

    Shared by HTTP (Request) and WebSocket paths. Trusts X-Forwarded-For
    only when the direct connection comes from a known proxy IP.
    """
    forwarded_for = (headers or {}).get("x-forwarded-for", "")
    if forwarded_for and direct_ip:
        if direct_ip in _get_trusted_ips():
            return forwarded_for.split(",")[0].strip()
    return direct_ip or "unknown"


def get_client_ip(request: Request) -> str:
    """Extract the real client IP from an HTTP request.

    Production requirement: Set FORWARDED_ALLOW_IPS to your reverse proxy's
    IP range, or configure uvicorn's --forwarded-allow-ips flag.
    """
    return resolve_client_ip(
        direct_ip=request.client.host if request.client else None,
        headers=dict(request.headers),
    )


limiter = Limiter(key_func=get_client_ip)


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Convert slowapi's RateLimitExceeded to the app error format."""
    return await app_error_handler(request, RateLimitError())
