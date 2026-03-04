"""Tests for authentication dependency."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.auth import _clerk_auth_cache, get_current_user_id
from app.core.exception_handlers import register_exception_handlers


def _create_test_app() -> FastAPI:
    """Create a minimal FastAPI app with the auth dependency."""
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/me")
    async def whoami(user_id: str = Depends(get_current_user_id)):
        return {"user_id": user_id}

    return test_app


PROD_JWKS = "https://clerk.example.com/.well-known/jwks.json"


def _mock_settings(clerk_jwks_url: str = ""):
    """Return a mock Settings object with the given clerk_jwks_url."""
    settings = MagicMock()
    settings.clerk_jwks_url = clerk_jwks_url
    return settings


class TestDevMode:
    """Auth in dev mode (empty clerk_jwks_url)."""

    @pytest.fixture
    def app(self):
        return _create_test_app()

    @pytest.fixture
    def client(self, app):
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    async def test_returns_user_id_from_header(self, client):
        with patch("app.core.auth.get_settings", return_value=_mock_settings("")):
            response = await client.get(
                "/me", headers={"x-user-id": "user-42"}
            )

        assert response.status_code == 200
        assert response.json() == {"user_id": "user-42"}

    async def test_raises_when_header_missing(self, client):
        with patch("app.core.auth.get_settings", return_value=_mock_settings("")):
            response = await client.get("/me")

        assert response.status_code == 401

    async def test_ignores_bearer_token_in_dev_mode(self, client):
        with patch("app.core.auth.get_settings", return_value=_mock_settings("")):
            response = await client.get(
                "/me",
                headers={
                    "x-user-id": "user-99",
                    "Authorization": "Bearer fake-token",
                },
            )

        assert response.status_code == 200
        assert response.json() == {"user_id": "user-99"}


class TestProdMode:
    """Auth in prod mode (clerk_jwks_url is set)."""

    @pytest.fixture(autouse=True)
    def _clear_clerk_cache(self):
        _clerk_auth_cache.clear()
        yield
        _clerk_auth_cache.clear()

    @pytest.fixture
    def app(self):
        return _create_test_app()

    @pytest.fixture
    def client(self, app):
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    async def test_raises_when_no_bearer_token(self, client):
        with patch(
            "app.core.auth.get_settings",
            return_value=_mock_settings(PROD_JWKS),
        ):
            response = await client.get(
                "/me", headers={"x-user-id": "user-1"}
            )

        assert response.status_code == 401

    async def test_returns_user_id_from_valid_token(self, client):
        mock_verified = MagicMock()
        mock_verified.decoded = {"sub": "user-clerk-123"}
        mock_clerk_auth = AsyncMock(return_value=mock_verified)

        with (
            patch("app.core.auth.get_settings", return_value=_mock_settings(PROD_JWKS)),
            patch("fastapi_clerk_auth.ClerkConfig"),
            patch("fastapi_clerk_auth.ClerkHTTPBearer", return_value=mock_clerk_auth),
        ):
            response = await client.get(
                "/me", headers={"Authorization": "Bearer valid-jwt"}
            )

        assert response.status_code == 200
        assert response.json() == {"user_id": "user-clerk-123"}

    async def test_reuses_cached_clerk_auth(self, client):
        mock_verified = MagicMock()
        mock_verified.decoded = {"sub": "user-clerk-456"}
        mock_clerk_auth = AsyncMock(return_value=mock_verified)

        with (
            patch("app.core.auth.get_settings", return_value=_mock_settings(PROD_JWKS)),
            patch("fastapi_clerk_auth.ClerkConfig"),
            patch("fastapi_clerk_auth.ClerkHTTPBearer", return_value=mock_clerk_auth) as mock_bearer_cls,
        ):
            # First request populates the cache
            r1 = await client.get(
                "/me", headers={"Authorization": "Bearer jwt-1"}
            )
            # Second request should reuse the cached instance
            r2 = await client.get(
                "/me", headers={"Authorization": "Bearer jwt-2"}
            )

        assert r1.status_code == 200
        assert r2.status_code == 200
        # ClerkHTTPBearer constructor called only once (cache hit on second)
        mock_bearer_cls.assert_called_once()

    async def test_raises_when_token_missing_sub(self, client):
        mock_verified = MagicMock()
        mock_verified.decoded = {"iss": "clerk"}
        mock_clerk_auth = AsyncMock(return_value=mock_verified)

        with (
            patch("app.core.auth.get_settings", return_value=_mock_settings(PROD_JWKS)),
            patch("fastapi_clerk_auth.ClerkConfig"),
            patch("fastapi_clerk_auth.ClerkHTTPBearer", return_value=mock_clerk_auth),
        ):
            response = await client.get(
                "/me", headers={"Authorization": "Bearer no-sub-jwt"}
            )

        assert response.status_code == 401

    async def test_raises_when_clerk_rejects_token(self, client):
        mock_clerk_auth = AsyncMock(side_effect=ValueError("bad token"))

        with (
            patch("app.core.auth.get_settings", return_value=_mock_settings(PROD_JWKS)),
            patch("fastapi_clerk_auth.ClerkConfig"),
            patch("fastapi_clerk_auth.ClerkHTTPBearer", return_value=mock_clerk_auth),
        ):
            response = await client.get(
                "/me", headers={"Authorization": "Bearer bad-jwt"}
            )

        assert response.status_code == 401
