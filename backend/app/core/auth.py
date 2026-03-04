"""Authentication dependency for FastAPI routes."""

from typing import Any

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.errors import AuthenticationError

# Optional bearer token - we handle missing token ourselves
_bearer_scheme = HTTPBearer(auto_error=False)


_clerk_auth_cache: dict[str, Any] = {}


async def _verify_clerk_token(
    request: Request, jwks_url: str
) -> str:
    """Validate a Bearer JWT against Clerk JWKS and return the user ID.

    Raises:
        AuthenticationError: If token is invalid or missing user identity.
    """
    try:
        from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer

        if jwks_url not in _clerk_auth_cache:
            config = ClerkConfig(jwks_url=jwks_url)
            _clerk_auth_cache[jwks_url] = ClerkHTTPBearer(config=config)
        clerk_auth = _clerk_auth_cache[jwks_url]
        verified = await clerk_auth(request)
        user_id = verified.decoded.get("sub")
        if not user_id:
            raise AuthenticationError(message="Token missing user identity")
        return user_id
    except AuthenticationError:
        raise
    except Exception as exc:
        raise AuthenticationError(message="Invalid or expired token") from exc


async def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    x_user_id: str | None = Header(None),
) -> str:
    """Extract and verify user_id from Bearer JWT or dev header.

    In production (clerk_jwks_url is set): validates Bearer token via Clerk JWKS.
    In development (clerk_jwks_url is empty): trusts X-User-ID header directly.

    Returns:
        The authenticated user's ID.

    Raises:
        AuthenticationError: If authentication fails.
    """
    settings = get_settings()

    # Dev mode: trust X-User-ID header when no JWKS URL configured
    if not settings.clerk_jwks_url:
        if not x_user_id:
            raise AuthenticationError(message="Missing X-User-ID header")
        return x_user_id

    # Production mode: validate Bearer token
    if not credentials:
        raise AuthenticationError(message="Missing Authorization header")

    return await _verify_clerk_token(request, settings.clerk_jwks_url)
