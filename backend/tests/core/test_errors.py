"""Tests for app.core.errors module."""

from app.core.errors import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    ExternalServiceError,
    NotFoundError,
    RateLimitError,
    StorageError,
    ValidationError,
)


class TestAppError:
    """Test the base AppError class."""

    def test_default_values(self):
        """AppError should have sensible defaults."""
        err = AppError()
        assert err.message == "An error occurred"
        assert err.error_code == "APP_ERROR"
        assert err.status_code == 500

    def test_custom_values(self):
        """AppError should accept custom values."""
        err = AppError(message="custom msg", error_code="CUSTOM", status_code=418)
        assert err.message == "custom msg"
        assert err.error_code == "CUSTOM"
        assert err.status_code == 418

    def test_str_representation(self):
        """AppError.__str__ should include error_code and message."""
        err = AppError(message="oops", error_code="MY_ERR")
        assert str(err) == "[MY_ERR] oops"

    def test_is_exception(self):
        """AppError should be an Exception subclass."""
        err = AppError()
        assert isinstance(err, Exception)


class TestValidationError:
    """Test ValidationError."""

    def test_defaults(self):
        err = ValidationError()
        assert err.message == "Validation failed"
        assert err.error_code == "VALIDATION_ERROR"
        assert err.status_code == 400

    def test_custom_message(self):
        err = ValidationError(message="bad input", error_code="BAD_INPUT")
        assert err.message == "bad input"
        assert err.error_code == "BAD_INPUT"
        assert err.status_code == 400


class TestNotFoundError:
    """Test NotFoundError."""

    def test_defaults(self):
        err = NotFoundError()
        assert err.message == "Resource not found"
        assert err.error_code == "NOT_FOUND"
        assert err.status_code == 404

    def test_custom_message(self):
        err = NotFoundError(message="User not found")
        assert err.message == "User not found"
        assert err.status_code == 404


class TestAuthenticationError:
    """Test AuthenticationError."""

    def test_defaults(self):
        err = AuthenticationError()
        assert err.message == "Authentication failed"
        assert err.error_code == "AUTHENTICATION_ERROR"
        assert err.status_code == 401

    def test_custom_message(self):
        err = AuthenticationError(message="Token expired")
        assert err.message == "Token expired"
        assert err.status_code == 401


class TestAuthorizationError:
    """Test AuthorizationError."""

    def test_defaults(self):
        err = AuthorizationError()
        assert err.message == "Authorization failed"
        assert err.error_code == "AUTHORIZATION_ERROR"
        assert err.status_code == 403

    def test_custom_message(self):
        err = AuthorizationError(message="Insufficient permissions")
        assert err.message == "Insufficient permissions"
        assert err.status_code == 403


class TestRateLimitError:
    """Test RateLimitError."""

    def test_defaults(self):
        err = RateLimitError()
        assert err.message == "Rate limit exceeded"
        assert err.error_code == "RATE_LIMIT_EXCEEDED"
        assert err.status_code == 429

    def test_custom_message(self):
        err = RateLimitError(message="Too many requests")
        assert err.message == "Too many requests"
        assert err.status_code == 429


class TestExternalServiceError:
    """Test ExternalServiceError."""

    def test_defaults(self):
        err = ExternalServiceError()
        assert err.message == "External service error"
        assert err.error_code == "EXTERNAL_SERVICE_ERROR"
        assert err.status_code == 502

    def test_custom_message(self):
        err = ExternalServiceError(message="Stripe is down")
        assert err.message == "Stripe is down"
        assert err.status_code == 502


class TestStorageError:
    """Test StorageError."""

    def test_defaults(self):
        err = StorageError()
        assert err.message == "Storage operation failed"
        assert err.error_code == "STORAGE_ERROR"
        assert err.status_code == 500

    def test_custom_message(self):
        err = StorageError(message="Disk full")
        assert err.message == "Disk full"
        assert err.status_code == 500
