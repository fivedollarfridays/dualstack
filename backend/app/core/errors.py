"""
Custom exception classes for standardized error handling.

All custom exceptions inherit from AppError and include:
- error_code: A unique code for the error type
- message: A human-readable error message
- status_code: HTTP status code for the error
"""


class AppError(Exception):
    """Base exception class for all application errors."""

    def __init__(
        self,
        message: str = "An error occurred",
        error_code: str = "APP_ERROR",
        status_code: int = 500,
    ):
        """Initialize AppError.

        Args:
            message: Human-readable error message
            error_code: Unique error code
            status_code: HTTP status code
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of error."""
        return f"[{self.error_code}] {self.message}"


class ValidationError(AppError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        error_code: str = "VALIDATION_ERROR",
    ):
        """Initialize ValidationError.

        Args:
            message: Human-readable error message
            error_code: Unique error code
        """
        super().__init__(message=message, error_code=error_code, status_code=400)


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
    ):
        """Initialize NotFoundError.

        Args:
            message: Human-readable error message
            error_code: Unique error code
        """
        super().__init__(message=message, error_code=error_code, status_code=404)


class AuthenticationError(AppError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "AUTHENTICATION_ERROR",
    ):
        """Initialize AuthenticationError.

        Args:
            message: Human-readable error message
            error_code: Unique error code
        """
        super().__init__(message=message, error_code=error_code, status_code=401)


class AuthorizationError(AppError):
    """Raised when user lacks required permissions."""

    def __init__(
        self,
        message: str = "Authorization failed",
        error_code: str = "AUTHORIZATION_ERROR",
    ):
        """Initialize AuthorizationError.

        Args:
            message: Human-readable error message
            error_code: Unique error code
        """
        super().__init__(message=message, error_code=error_code, status_code=403)


class RateLimitError(AppError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        error_code: str = "RATE_LIMIT_EXCEEDED",
    ):
        """Initialize RateLimitError.

        Args:
            message: Human-readable error message
            error_code: Unique error code
        """
        super().__init__(message=message, error_code=error_code, status_code=429)


class ExternalServiceError(AppError):
    """Raised when an external service call fails."""

    def __init__(
        self,
        message: str = "External service error",
        error_code: str = "EXTERNAL_SERVICE_ERROR",
    ):
        """Initialize ExternalServiceError.

        Args:
            message: Human-readable error message
            error_code: Unique error code
        """
        super().__init__(message=message, error_code=error_code, status_code=502)


class StorageError(AppError):
    """Raised when storage operations fail."""

    def __init__(
        self,
        message: str = "Storage operation failed",
        error_code: str = "STORAGE_ERROR",
    ):
        """Initialize StorageError.

        Args:
            message: Human-readable error message
            error_code: Unique error code
        """
        super().__init__(message=message, error_code=error_code, status_code=500)


class ServiceUnavailableError(AppError):
    """Raised when a required service is not configured or available."""

    def __init__(
        self,
        message: str = "Service unavailable",
        error_code: str = "SERVICE_UNAVAILABLE",
    ):
        """Initialize ServiceUnavailableError.

        Args:
            message: Human-readable error message
            error_code: Unique error code
        """
        super().__init__(message=message, error_code=error_code, status_code=503)
