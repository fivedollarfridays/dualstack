"""
Exception handlers for FastAPI application.

Provides standardized error responses for all application exceptions.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.errors import AppError
from app.core.logging import get_logger

logger = get_logger(__name__)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle custom AppError exceptions.

    Args:
        request: The incoming request
        exc: The AppError exception

    Returns:
        JSONResponse with error details
    """
    logger.warning(
        "app_error",
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.error_code, "message": exc.message}},
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    Args:
        request: The incoming request
        exc: The exception

    Returns:
        JSONResponse with generic error message
    """
    logger.exception(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
            }
        },
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors without leaking field details."""
    logger.warning(
        "validation_error",
        path=request.url.path,
        error_count=len(exc.errors()),
    )

    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": "Invalid request"}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app.

    Args:
        app: The FastAPI application instance
    """
    # Custom app errors
    app.add_exception_handler(AppError, app_error_handler)

    # Pydantic validation errors (sanitized)
    app.add_exception_handler(RequestValidationError, validation_error_handler)

    # Generic unexpected errors
    app.add_exception_handler(Exception, generic_error_handler)
