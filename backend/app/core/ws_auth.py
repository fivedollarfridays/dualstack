"""WebSocket authentication — verify token from first-message or query param."""

import asyncio
import logging
from collections import OrderedDict
from typing import Any

import jwt as pyjwt
from jwt import PyJWKClient

from app.core.config import get_settings
from app.core.errors import AuthenticationError

logger = logging.getLogger(__name__)

MAX_JWK_CACHE_SIZE = 10

# Bounded LRU cache for PyJWKClient instances (keyed by JWKS URL)
_jwk_client_cache: OrderedDict[str, Any] = OrderedDict()


def _get_jwk_client(jwks_url: str) -> PyJWKClient:
    """Return a cached PyJWKClient for the given JWKS URL."""
    if jwks_url not in _jwk_client_cache:
        if len(_jwk_client_cache) >= MAX_JWK_CACHE_SIZE:
            _jwk_client_cache.popitem(last=False)
        _jwk_client_cache[jwks_url] = PyJWKClient(jwks_url)
    _jwk_client_cache.move_to_end(jwks_url)
    return _jwk_client_cache[jwks_url]


async def _verify_token(token: str, jwks_url: str) -> str:
    """Verify a JWT token signature via JWKS and return the user ID.

    Uses PyJWKClient to fetch the signing key from the Clerk JWKS endpoint,
    then decodes and validates the JWT with full signature verification.
    """
    try:
        settings = get_settings()
        client = _get_jwk_client(jwks_url)
        signing_key = await asyncio.to_thread(client.get_signing_key_from_jwt, token)
        decode_kwargs: dict[str, Any] = {}
        if settings.clerk_audience:
            decode_kwargs["audience"] = settings.clerk_audience
        else:
            decode_kwargs["options"] = {"verify_aud": False}
        decoded = pyjwt.decode(
            token, signing_key.key, algorithms=["RS256"], **decode_kwargs
        )
        user_id = decoded.get("sub")
        if not user_id:
            raise AuthenticationError(message="Token missing user identity")
        return user_id
    except AuthenticationError:
        raise
    except Exception as exc:
        raise AuthenticationError(message="Invalid or expired token") from exc


async def authenticate_ws_from_message(token: str) -> str:
    """Authenticate a WebSocket connection from a first-message JWT.

    In dev mode (no clerk_jwks_url): treats token as user_id directly.
    In production: validates the JWT via JWKS.
    """
    settings = get_settings()

    if not token:
        raise AuthenticationError(message="Token is required")

    if not settings.clerk_jwks_url:
        if settings.environment == "production":
            raise AuthenticationError(message="Dev-mode auth is disabled in production")
        return token

    return await _verify_token(token, settings.clerk_jwks_url)
