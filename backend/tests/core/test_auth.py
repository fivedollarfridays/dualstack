"""Tests for authentication dependency."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.auth import _clerk_auth_cache, get_current_user_id
from app.core.exception_handlers import register_exception_handlers


class TestAuthAuditEvents:
    """NEW-006: Auth failures should emit audit events."""

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

    async def test_audit_on_missing_header_dev_mode(self, client):
        """Missing X-User-ID in dev mode should emit audit event."""
        with (
            patch("app.core.auth.get_settings", return_value=_mock_settings("")),
            patch("app.core.auth.log_audit_event") as mock_audit,
        ):
            await client.get("/me")
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs["outcome"] == "failure"
            assert kwargs["action"] == "auth.missing_header"

    async def test_audit_on_dev_mode_rejected_in_prod(self, client):
        """Dev-mode auth rejected in production should emit audit event."""
        with (
            patch(
                "app.core.auth.get_settings",
                return_value=_mock_settings("", environment="production"),
            ),
            patch("app.core.auth.log_audit_event") as mock_audit,
        ):
            await client.get("/me", headers={"x-user-id": "user-42"})
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs["outcome"] == "failure"
            assert kwargs["action"] == "auth.dev_mode_rejected"

    async def test_audit_on_missing_bearer_token(self, client):
        """Missing Authorization header in prod mode should emit audit event."""
        with (
            patch(
                "app.core.auth.get_settings",
                return_value=_mock_settings(PROD_JWKS),
            ),
            patch("app.core.auth.log_audit_event") as mock_audit,
        ):
            await client.get("/me", headers={"x-user-id": "user-1"})
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs["outcome"] == "failure"
            assert kwargs["action"] == "auth.missing_token"

    async def test_audit_on_invalid_jwt(self, client):
        """Invalid JWT should emit audit event."""
        mock_clerk_auth = AsyncMock(side_effect=ValueError("bad token"))

        with (
            patch(
                "app.core.auth.get_settings",
                return_value=_mock_settings(PROD_JWKS),
            ),
            patch("app.core.auth.ClerkConfig"),
            patch("app.core.auth.ClerkHTTPBearer", return_value=mock_clerk_auth),
            patch("app.core.auth.log_audit_event") as mock_audit,
        ):
            await client.get("/me", headers={"Authorization": "Bearer bad-jwt"})
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs["outcome"] == "failure"
            assert kwargs["action"] == "auth.invalid_token"

    async def test_audit_on_missing_sub_claim(self, client):
        """Token missing sub claim should emit audit event."""
        mock_verified = MagicMock()
        mock_verified.decoded = {"iss": "clerk"}
        mock_clerk_auth = AsyncMock(return_value=mock_verified)

        with (
            patch(
                "app.core.auth.get_settings",
                return_value=_mock_settings(PROD_JWKS),
            ),
            patch("app.core.auth.ClerkConfig"),
            patch("app.core.auth.ClerkHTTPBearer", return_value=mock_clerk_auth),
            patch("app.core.auth.log_audit_event") as mock_audit,
        ):
            await client.get("/me", headers={"Authorization": "Bearer no-sub-jwt"})
            mock_audit.assert_called_once()
            kwargs = mock_audit.call_args[1]
            assert kwargs["outcome"] == "failure"
            assert kwargs["action"] == "auth.missing_identity"


def _create_test_app() -> FastAPI:
    """Create a minimal FastAPI app with the auth dependency."""
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/me")
    async def whoami(user_id: str = Depends(get_current_user_id)):
        return {"user_id": user_id}

    return test_app


PROD_JWKS = "https://clerk.example.com/.well-known/jwks.json"


def _mock_settings(
    clerk_jwks_url: str = "",
    environment: str = "development",
    clerk_audience: str = "",
):
    """Return a mock Settings object with the given clerk_jwks_url."""
    settings = MagicMock()
    settings.clerk_jwks_url = clerk_jwks_url
    settings.environment = environment
    settings.clerk_audience = clerk_audience
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
            response = await client.get("/me", headers={"x-user-id": "user-42"})

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

    async def test_rejects_dev_bypass_in_production(self, client):
        """SEC-001: Dev bypass must be rejected when environment=production."""
        with patch(
            "app.core.auth.get_settings",
            return_value=_mock_settings("", environment="production"),
        ):
            response = await client.get("/me", headers={"x-user-id": "user-42"})

        assert response.status_code == 401

    async def test_allows_dev_bypass_in_development(self, client):
        """SEC-001: Dev bypass allowed when environment=development."""
        with patch(
            "app.core.auth.get_settings",
            return_value=_mock_settings("", environment="development"),
        ):
            response = await client.get("/me", headers={"x-user-id": "user-42"})

        assert response.status_code == 200
        assert response.json() == {"user_id": "user-42"}


class TestAuthCacheBounds:
    """AUDIT-011: _clerk_auth_cache must have a max size."""

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

    async def test_cache_evicts_oldest_when_max_size_exceeded(self, client):
        """Cache should evict oldest entries when exceeding MAX_CACHE_SIZE."""
        from app.core.auth import MAX_CACHE_SIZE

        # Pre-fill the cache to max capacity
        for i in range(MAX_CACHE_SIZE):
            _clerk_auth_cache[f"https://jwks-{i}.example.com"] = f"auth-{i}"

        assert len(_clerk_auth_cache) == MAX_CACHE_SIZE
        first_key = "https://jwks-0.example.com"
        assert first_key in _clerk_auth_cache

        # Make a request with a new JWKS URL to trigger eviction
        new_jwks = "https://new-jwks.example.com/.well-known/jwks.json"
        mock_verified = MagicMock()
        mock_verified.decoded = {"sub": "user-evict"}
        mock_clerk_auth = AsyncMock(return_value=mock_verified)

        with (
            patch("app.core.auth.get_settings", return_value=_mock_settings(new_jwks)),
            patch("app.core.auth.ClerkConfig"),
            patch("app.core.auth.ClerkHTTPBearer", return_value=mock_clerk_auth),
        ):
            r = await client.get("/me", headers={"Authorization": "Bearer jwt"})

        assert r.status_code == 200
        # Cache should still be at max, not above
        assert len(_clerk_auth_cache) == MAX_CACHE_SIZE
        # Oldest entry should have been evicted
        assert first_key not in _clerk_auth_cache
        # New entry should be present (cache key includes audience suffix)
        new_cache_key = f"{new_jwks}|"
        assert new_cache_key in _clerk_auth_cache


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
            response = await client.get("/me", headers={"x-user-id": "user-1"})

        assert response.status_code == 401

    async def test_returns_user_id_from_valid_token(self, client):
        mock_verified = MagicMock()
        mock_verified.decoded = {"sub": "user-clerk-123"}
        mock_clerk_auth = AsyncMock(return_value=mock_verified)

        with (
            patch("app.core.auth.get_settings", return_value=_mock_settings(PROD_JWKS)),
            patch("app.core.auth.ClerkConfig"),
            patch("app.core.auth.ClerkHTTPBearer", return_value=mock_clerk_auth),
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
            patch("app.core.auth.ClerkConfig"),
            patch(
                "app.core.auth.ClerkHTTPBearer", return_value=mock_clerk_auth
            ) as mock_bearer_cls,
        ):
            # First request populates the cache
            r1 = await client.get("/me", headers={"Authorization": "Bearer jwt-1"})
            # Second request should reuse the cached instance
            r2 = await client.get("/me", headers={"Authorization": "Bearer jwt-2"})

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
            patch("app.core.auth.ClerkConfig"),
            patch("app.core.auth.ClerkHTTPBearer", return_value=mock_clerk_auth),
        ):
            response = await client.get(
                "/me", headers={"Authorization": "Bearer no-sub-jwt"}
            )

        assert response.status_code == 401

    async def test_raises_when_clerk_rejects_token(self, client):
        mock_clerk_auth = AsyncMock(side_effect=ValueError("bad token"))

        with (
            patch("app.core.auth.get_settings", return_value=_mock_settings(PROD_JWKS)),
            patch("app.core.auth.ClerkConfig"),
            patch("app.core.auth.ClerkHTTPBearer", return_value=mock_clerk_auth),
        ):
            response = await client.get(
                "/me", headers={"Authorization": "Bearer bad-jwt"}
            )

        assert response.status_code == 401


class TestAudienceEnforcement:
    """T26.1: HTTP auth must validate JWT audience when CLERK_AUDIENCE is set."""

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

    async def test_audience_passed_to_clerk_config(self, client):
        """When clerk_audience is set, it should be passed to ClerkConfig."""
        mock_verified = MagicMock()
        mock_verified.decoded = {"sub": "user-aud-ok"}
        mock_clerk_auth = AsyncMock(return_value=mock_verified)
        audience = "https://my-app.example.com"

        with (
            patch(
                "app.core.auth.get_settings",
                return_value=_mock_settings(PROD_JWKS, clerk_audience=audience),
            ),
            patch("app.core.auth.ClerkConfig") as mock_config_cls,
            patch("app.core.auth.ClerkHTTPBearer", return_value=mock_clerk_auth),
        ):
            response = await client.get(
                "/me", headers={"Authorization": "Bearer valid-jwt"}
            )

        assert response.status_code == 200
        mock_config_cls.assert_called_once_with(
            jwks_url=PROD_JWKS, audience=audience
        )

    async def test_audience_not_passed_when_empty(self, client):
        """When clerk_audience is empty, ClerkConfig should NOT get audience."""
        mock_verified = MagicMock()
        mock_verified.decoded = {"sub": "user-no-aud"}
        mock_clerk_auth = AsyncMock(return_value=mock_verified)

        with (
            patch(
                "app.core.auth.get_settings",
                return_value=_mock_settings(PROD_JWKS, clerk_audience=""),
            ),
            patch("app.core.auth.ClerkConfig") as mock_config_cls,
            patch("app.core.auth.ClerkHTTPBearer", return_value=mock_clerk_auth),
        ):
            response = await client.get(
                "/me", headers={"Authorization": "Bearer valid-jwt"}
            )

        assert response.status_code == 200
        mock_config_cls.assert_called_once_with(jwks_url=PROD_JWKS)

    async def test_audience_mismatch_rejected(self, client):
        """When audience validation fails, auth should return 401."""
        mock_clerk_auth = AsyncMock(
            side_effect=ValueError("Audience mismatch")
        )

        with (
            patch(
                "app.core.auth.get_settings",
                return_value=_mock_settings(
                    PROD_JWKS, clerk_audience="https://my-app.example.com"
                ),
            ),
            patch("app.core.auth.ClerkConfig"),
            patch("app.core.auth.ClerkHTTPBearer", return_value=mock_clerk_auth),
        ):
            response = await client.get(
                "/me", headers={"Authorization": "Bearer wrong-aud-jwt"}
            )

        assert response.status_code == 401

    async def test_dev_mode_unaffected_by_audience(self, client):
        """Dev mode should work regardless of clerk_audience setting."""
        with patch(
            "app.core.auth.get_settings",
            return_value=_mock_settings(
                "", clerk_audience="https://my-app.example.com"
            ),
        ):
            response = await client.get("/me", headers={"x-user-id": "dev-user"})

        assert response.status_code == 200
        assert response.json() == {"user_id": "dev-user"}
