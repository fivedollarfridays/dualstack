"""Tests for WebSocket authentication."""

import time
from unittest.mock import MagicMock, patch

import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.errors import AuthenticationError


# ---------------------------------------------------------------------------
# RSA key helpers for test JWTs
# ---------------------------------------------------------------------------


def _generate_rsa_keypair():
    """Generate an RSA private key for signing test JWTs."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key


def _make_jwt(private_key, claims: dict) -> str:
    """Create a signed RS256 JWT from claims."""
    return pyjwt.encode(claims, private_key, algorithm="RS256")


# ---------------------------------------------------------------------------
# _verify_token — signature verification tests
# ---------------------------------------------------------------------------


class TestVerifyToken:
    """Tests for _verify_token — must enforce JWT signature verification."""

    @pytest.fixture(autouse=True)
    def _clear_jwk_cache(self):
        """Clear the JWKS client cache between tests."""
        from app.core import ws_auth

        ws_auth._jwk_client_cache.clear()

    async def test_valid_token_returns_user_id(self):
        """A correctly signed JWT with sub claim returns user_id."""
        from app.core.ws_auth import _verify_token

        key = _generate_rsa_keypair()
        token = _make_jwt(key, {"sub": "user-123", "exp": int(time.time()) + 300})

        # Mock PyJWKClient to return the correct public key
        mock_jwk = MagicMock()
        mock_jwk.key = key.public_key()

        with patch("app.core.ws_auth.PyJWKClient") as MockClient:
            client_instance = MagicMock()
            client_instance.get_signing_key_from_jwt.return_value = mock_jwk
            MockClient.return_value = client_instance

            result = await _verify_token(
                token, "https://clerk.example.com/.well-known/jwks.json"
            )

        assert result == "user-123"

    async def test_forged_token_rejected(self):
        """A JWT signed with the wrong key must be rejected."""
        from app.core.ws_auth import _verify_token

        legit_key = _generate_rsa_keypair()
        wrong_key = _generate_rsa_keypair()
        token = _make_jwt(
            wrong_key, {"sub": "user-evil", "exp": int(time.time()) + 300}
        )

        # JWKS returns the legit public key — token was signed with wrong_key
        mock_jwk = MagicMock()
        mock_jwk.key = legit_key.public_key()

        with patch("app.core.ws_auth.PyJWKClient") as MockClient:
            client_instance = MagicMock()
            client_instance.get_signing_key_from_jwt.return_value = mock_jwk
            MockClient.return_value = client_instance

            with pytest.raises(AuthenticationError, match="Invalid or expired token"):
                await _verify_token(
                    token, "https://clerk.example.com/.well-known/jwks.json"
                )

    async def test_expired_token_rejected(self):
        """An expired JWT must be rejected even if signature is valid."""
        from app.core.ws_auth import _verify_token

        key = _generate_rsa_keypair()
        token = _make_jwt(key, {"sub": "user-123", "exp": int(time.time()) - 60})

        mock_jwk = MagicMock()
        mock_jwk.key = key.public_key()

        with patch("app.core.ws_auth.PyJWKClient") as MockClient:
            client_instance = MagicMock()
            client_instance.get_signing_key_from_jwt.return_value = mock_jwk
            MockClient.return_value = client_instance

            with pytest.raises(AuthenticationError, match="Invalid or expired token"):
                await _verify_token(
                    token, "https://clerk.example.com/.well-known/jwks.json"
                )

    async def test_missing_sub_claim_rejected(self):
        """A valid JWT without sub claim must be rejected."""
        from app.core.ws_auth import _verify_token

        key = _generate_rsa_keypair()
        token = _make_jwt(key, {"exp": int(time.time()) + 300})

        mock_jwk = MagicMock()
        mock_jwk.key = key.public_key()

        with patch("app.core.ws_auth.PyJWKClient") as MockClient:
            client_instance = MagicMock()
            client_instance.get_signing_key_from_jwt.return_value = mock_jwk
            MockClient.return_value = client_instance

            with pytest.raises(
                AuthenticationError, match="Token missing user identity"
            ):
                await _verify_token(
                    token, "https://clerk.example.com/.well-known/jwks.json"
                )

    async def test_wrong_audience_rejected(self):
        """A JWT with wrong audience must be rejected when clerk_audience is set."""
        from app.core.ws_auth import _verify_token

        key = _generate_rsa_keypair()
        token = _make_jwt(
            key,
            {
                "sub": "user-123",
                "aud": "wrong-app",
                "exp": int(time.time()) + 300,
            },
        )

        mock_jwk = MagicMock()
        mock_jwk.key = key.public_key()

        with patch("app.core.ws_auth.PyJWKClient") as MockClient:
            client_instance = MagicMock()
            client_instance.get_signing_key_from_jwt.return_value = mock_jwk
            MockClient.return_value = client_instance

            with patch("app.core.ws_auth.get_settings") as mock_settings:
                settings = MagicMock()
                settings.clerk_audience = "my-app"
                mock_settings.return_value = settings

                with pytest.raises(
                    AuthenticationError, match="Invalid or expired token"
                ):
                    await _verify_token(
                        token, "https://clerk.example.com/.well-known/jwks.json"
                    )

    async def test_correct_audience_accepted(self):
        """A JWT with matching audience must be accepted when clerk_audience is set."""
        from app.core.ws_auth import _verify_token

        key = _generate_rsa_keypair()
        token = _make_jwt(
            key,
            {
                "sub": "user-123",
                "aud": "my-app",
                "exp": int(time.time()) + 300,
            },
        )

        mock_jwk = MagicMock()
        mock_jwk.key = key.public_key()

        with patch("app.core.ws_auth.PyJWKClient") as MockClient:
            client_instance = MagicMock()
            client_instance.get_signing_key_from_jwt.return_value = mock_jwk
            MockClient.return_value = client_instance

            with patch("app.core.ws_auth.get_settings") as mock_settings:
                settings = MagicMock()
                settings.clerk_audience = "my-app"
                mock_settings.return_value = settings

                result = await _verify_token(
                    token, "https://clerk.example.com/.well-known/jwks.json"
                )

        assert result == "user-123"

    async def test_audience_not_checked_when_empty(self):
        """When clerk_audience is empty, audience claim is not validated (dev compat)."""
        from app.core.ws_auth import _verify_token

        key = _generate_rsa_keypair()
        token = _make_jwt(
            key,
            {
                "sub": "user-456",
                "aud": "any-app",
                "exp": int(time.time()) + 300,
            },
        )

        mock_jwk = MagicMock()
        mock_jwk.key = key.public_key()

        with patch("app.core.ws_auth.PyJWKClient") as MockClient:
            client_instance = MagicMock()
            client_instance.get_signing_key_from_jwt.return_value = mock_jwk
            MockClient.return_value = client_instance

            with patch("app.core.ws_auth.get_settings") as mock_settings:
                settings = MagicMock()
                settings.clerk_audience = ""
                mock_settings.return_value = settings

                result = await _verify_token(
                    token, "https://clerk.example.com/.well-known/jwks.json"
                )

        assert result == "user-456"

    async def test_jwk_client_cached_per_url(self):
        """PyJWKClient instances should be cached by JWKS URL."""
        from app.core.ws_auth import _verify_token

        key = _generate_rsa_keypair()
        token = _make_jwt(key, {"sub": "user-1", "exp": int(time.time()) + 300})

        mock_jwk = MagicMock()
        mock_jwk.key = key.public_key()

        with patch("app.core.ws_auth.PyJWKClient") as MockClient:
            client_instance = MagicMock()
            client_instance.get_signing_key_from_jwt.return_value = mock_jwk
            MockClient.return_value = client_instance

            url = "https://clerk.example.com/.well-known/jwks.json"
            await _verify_token(token, url)
            await _verify_token(token, url)

            # PyJWKClient should only be instantiated once for the same URL
            assert MockClient.call_count == 1


# ---------------------------------------------------------------------------
# authenticate_ws_from_message — first-message auth pattern
# ---------------------------------------------------------------------------


class TestAuthenticateWsFromMessage:
    """Tests for authenticate_ws_from_message — takes raw JWT string."""

    @pytest.fixture(autouse=True)
    def _clear_jwk_cache(self):
        from app.core import ws_auth

        ws_auth._jwk_client_cache.clear()

    async def test_valid_token_returns_user_id(self):
        """A valid JWT string returns the user_id."""
        from app.core.ws_auth import authenticate_ws_from_message

        key = _generate_rsa_keypair()
        token = _make_jwt(key, {"sub": "user-msg-1", "exp": int(time.time()) + 300})

        mock_jwk = MagicMock()
        mock_jwk.key = key.public_key()

        with patch("app.core.ws_auth.PyJWKClient") as MockClient:
            client_instance = MagicMock()
            client_instance.get_signing_key_from_jwt.return_value = mock_jwk
            MockClient.return_value = client_instance

            with patch("app.core.ws_auth.get_settings") as mock_settings:
                settings = MagicMock()
                settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
                settings.clerk_audience = ""
                mock_settings.return_value = settings

                result = await authenticate_ws_from_message(token)

        assert result == "user-msg-1"

    async def test_invalid_token_raises(self):
        """An invalid JWT string raises AuthenticationError."""
        from app.core.ws_auth import authenticate_ws_from_message

        with patch("app.core.ws_auth.get_settings") as mock_settings:
            settings = MagicMock()
            settings.clerk_jwks_url = "https://clerk.example.com/.well-known/jwks.json"
            mock_settings.return_value = settings

            with patch("app.core.ws_auth._verify_token") as mock_verify:
                mock_verify.side_effect = AuthenticationError(
                    message="Invalid or expired token"
                )

                with pytest.raises(AuthenticationError):
                    await authenticate_ws_from_message("bad-jwt")

    async def test_dev_mode_user_id_returns_directly(self):
        """In dev mode (no JWKS URL), the token is treated as user_id."""
        from app.core.ws_auth import authenticate_ws_from_message

        with patch("app.core.ws_auth.get_settings") as mock_settings:
            settings = MagicMock()
            settings.clerk_jwks_url = ""
            settings.environment = "development"
            mock_settings.return_value = settings

            result = await authenticate_ws_from_message("dev-user-123")

        assert result == "dev-user-123"

    async def test_dev_mode_rejected_in_production(self):
        """Dev mode auth via first-message is rejected in production."""
        from app.core.ws_auth import authenticate_ws_from_message

        with patch("app.core.ws_auth.get_settings") as mock_settings:
            settings = MagicMock()
            settings.clerk_jwks_url = ""
            settings.environment = "production"
            mock_settings.return_value = settings

            with pytest.raises(AuthenticationError):
                await authenticate_ws_from_message("dev-user-123")
