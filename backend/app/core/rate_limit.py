"""Rate limiting configuration using slowapi."""

from fastapi import Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.errors import RateLimitError
from app.core.exception_handlers import app_error_handler

limiter = Limiter(key_func=get_remote_address)


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Convert slowapi's RateLimitExceeded to the app error format."""
    return await app_error_handler(request, RateLimitError())
