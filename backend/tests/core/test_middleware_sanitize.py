"""Tests for query param sanitization in middleware (S-11)."""

import pytest
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from app.core.middleware import LoggingMiddleware, _sanitize_params


class TestSanitizeParams:
    """Test _sanitize_params helper function."""

    def test_redacts_token_param(self):
        """Should redact 'token' parameter."""
        result = _sanitize_params({"token": "abc123", "page": "1"})
        assert result == {"token": "***", "page": "1"}

    def test_redacts_key_param(self):
        """Should redact 'key' parameter."""
        result = _sanitize_params({"key": "my-secret"})
        assert result == {"key": "***"}

    def test_redacts_secret_param(self):
        """Should redact 'secret' parameter."""
        result = _sanitize_params({"secret": "s3cr3t"})
        assert result == {"secret": "***"}

    def test_redacts_password_param(self):
        """Should redact 'password' parameter."""
        result = _sanitize_params({"password": "hunter2"})
        assert result == {"password": "***"}

    def test_redacts_api_key_param(self):
        """Should redact 'api_key' parameter."""
        result = _sanitize_params({"api_key": "key-123"})
        assert result == {"api_key": "***"}

    def test_redacts_access_token_param(self):
        """Should redact 'access_token' parameter."""
        result = _sanitize_params({"access_token": "tok-xyz"})
        assert result == {"access_token": "***"}

    def test_case_insensitive_redaction(self):
        """Should redact regardless of case."""
        result = _sanitize_params({"TOKEN": "abc", "Password": "xyz"})
        assert result == {"TOKEN": "***", "Password": "***"}

    def test_preserves_safe_params(self):
        """Should not redact non-sensitive params."""
        result = _sanitize_params({"page": "1", "limit": "20", "search": "test"})
        assert result == {"page": "1", "limit": "20", "search": "test"}

    def test_redacts_auth_param(self):
        """Should redact 'auth' parameter."""
        result = _sanitize_params({"auth": "bearer-token"})
        assert result == {"auth": "***"}

    def test_redacts_authorization_param(self):
        """Should redact 'authorization' parameter."""
        result = _sanitize_params({"authorization": "Bearer xyz"})
        assert result == {"authorization": "***"}

    def test_redacts_apikey_param(self):
        """Should redact 'apikey' parameter."""
        result = _sanitize_params({"apikey": "key-456"})
        assert result == {"apikey": "***"}

    def test_redacts_code_param(self):
        """Should redact 'code' parameter."""
        result = _sanitize_params({"code": "auth-code-123"})
        assert result == {"code": "***"}

    def test_redacts_state_param(self):
        """Should redact 'state' parameter."""
        result = _sanitize_params({"state": "csrf-state"})
        assert result == {"state": "***"}

    def test_redacts_client_secret_param(self):
        """Should redact 'client_secret' parameter."""
        result = _sanitize_params({"client_secret": "secret-value"})
        assert result == {"client_secret": "***"}

    def test_empty_params(self):
        """Should handle empty dict."""
        result = _sanitize_params({})
        assert result == {}


class TestMiddlewareSanitization:
    """Test that middleware uses sanitized params in log output."""

    @pytest.mark.asyncio
    async def test_sensitive_params_redacted_in_log(self):
        """Sensitive query params should be redacted in request log."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)

        @app.get("/test")
        async def test_route():
            return {"ok": True}

        with patch("app.core.middleware.logger") as mock_logger:
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                await client.get("/test?token=secret123&page=1")

            # Find the request_started log call
            started_calls = [
                c
                for c in mock_logger.info.call_args_list
                if c.args and c.args[0] == "request_started"
            ]
            assert len(started_calls) >= 1
            kwargs = started_calls[0].kwargs
            assert kwargs["query_params"]["token"] == "***"
            assert kwargs["query_params"]["page"] == "1"
