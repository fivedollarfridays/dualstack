"""Authentication dependency for FastAPI routes."""

from typing import Any

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.audit import log_audit_event
from app.core.config import get_settings
from app.core.errors import AuthenticationError

# Optional bearer token - we handle missing token ourselves
_bearer_scheme = HTTPBearer(auto_error=False)


# Bounded by unique JWKS URLs (typically 1 per deployment)
_clerk_auth_cache: dict[str, Any] = {}


def _audit_auth_failure(action: str, user_id: str = "unknown") -> None:
    """Log an auth failure audit event."""
    log_audit_event(
        user_id=user_id, action=action,
        resource_type="token", resource_id="unknown", outcome="failure",
    )


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
            _audit_auth_failure("auth.missing_identity")
            raise AuthenticationError(message="Token missing user identity")
        return user_id
    except AuthenticationError:
        raise
    except Exception as exc:
        _audit_auth_failure("auth.invalid_token")
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
        if settings.environment == "production":
            _audit_auth_failure("auth.dev_mode_rejected", x_user_id or "unknown")
            raise AuthenticationError(
                message="Dev-mode auth is disabled in production. Set CLERK_JWKS_URL."
            )
        if not x_user_id:
            _audit_auth_failure("auth.missing_header")
            raise AuthenticationError(message="Missing X-User-ID header")
        return x_user_id

    # Production mode: validate Bearer token
    if not credentials:
        _audit_auth_failure("auth.missing_token")
        raise AuthenticationError(message="Missing Authorization header")

    return await _verify_clerk_token(request, settings.clerk_jwks_url)
