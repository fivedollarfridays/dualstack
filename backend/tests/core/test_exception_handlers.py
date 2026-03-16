"""Tests for app.core.exception_handlers module."""

import json
from unittest.mock import MagicMock

import pytest

from app.core.errors import AppError, NotFoundError, ValidationError
from app.core.exception_handlers import (
    app_error_handler,
    generic_error_handler,
    register_exception_handlers,
)


def _make_request(path: str = "/test") -> MagicMock:
    """Create a mock Request with a url.path attribute."""
    request = MagicMock()
    request.url.path = path
    return request


class TestAppErrorHandler:
    """Test app_error_handler."""

    @pytest.mark.asyncio
    async def test_returns_correct_status_code(self):
        """Should return the status code from the AppError."""
        request = _make_request()
        exc = NotFoundError(message="Item not found")
        response = await app_error_handler(request, exc)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_error_json(self):
        """Should return JSON body with error code and message."""
        request = _make_request()
        exc = ValidationError(message="Invalid email")
        response = await app_error_handler(request, exc)
        body = json.loads(response.body)
        assert body["error"]["code"] == "VALIDATION_ERROR"
        assert body["error"]["message"] == "Invalid email"

    @pytest.mark.asyncio
    async def test_with_base_app_error(self):
        """Should handle base AppError with defaults."""
        request = _make_request("/api/v1/items")
        exc = AppError()
        response = await app_error_handler(request, exc)
        assert response.status_code == 500
        body = json.loads(response.body)
        assert body["error"]["code"] == "APP_ERROR"


class TestGenericErrorHandler:
    """Test generic_error_handler."""

    @pytest.mark.asyncio
    async def test_returns_500(self):
        """Should return 500 for unexpected exceptions."""
        request = _make_request()
        exc = RuntimeError("something went wrong")
        response = await generic_error_handler(request, exc)
        assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_returns_internal_error_code(self):
        """Should return INTERNAL_ERROR code."""
        request = _make_request()
        exc = ValueError("bad value")
        response = await generic_error_handler(request, exc)
        body = json.loads(response.body)
        assert body["error"]["code"] == "INTERNAL_ERROR"
        assert body["error"]["message"] == "An internal error occurred"


class TestValidationErrorHandler:
    """NEW-004: 422 validation errors should not leak field details."""

    @pytest.mark.asyncio
    async def test_sanitized_422_response(self):
        """RequestValidationError should return sanitized response without field details."""
        from fastapi.exceptions import RequestValidationError
        from app.core.exception_handlers import validation_error_handler

        request = _make_request()
        exc = RequestValidationError(
            errors=[
                {
                    "loc": ["body", "price_id"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        )
        response = await validation_error_handler(request, exc)
        assert response.status_code == 422
        body = json.loads(response.body)
        assert body["error"]["code"] == "VALIDATION_ERROR"
        assert body["error"]["message"] == "Invalid request"
        assert "loc" not in json.dumps(body)
        assert "price_id" not in json.dumps(body)


class TestRegisterExceptionHandlers:
    """Test register_exception_handlers."""

    def test_registers_all_handlers(self):
        """Should register handlers for AppError, Exception, and RequestValidationError."""
        from fastapi.exceptions import RequestValidationError

        mock_app = MagicMock()
        register_exception_handlers(mock_app)
        assert mock_app.add_exception_handler.call_count == 3
        calls = mock_app.add_exception_handler.call_args_list
        registered_types = {call.args[0] for call in calls}
        assert AppError in registered_types
        assert Exception in registered_types
        assert RequestValidationError in registered_types
