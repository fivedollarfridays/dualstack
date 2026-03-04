"""Logging middleware for request/response logging."""

import re
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars

from app.core.logging import get_logger
from app.core.metrics import increment_http_requests, observe_http_duration

logger = get_logger(__name__)

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

SENSITIVE_PARAMS = {
    "token", "key", "secret", "password", "api_key", "access_token",
    "auth", "authorization", "apikey", "code", "state",
    "client_secret", "private_key", "credential",
}


def _sanitize_params(params: dict) -> dict:
    """Redact sensitive query parameters for safe logging.

    Args:
        params: Dictionary of query parameter key-value pairs.

    Returns:
        Copy with sensitive values replaced by '***'.
    """
    return {
        k: "***" if k.lower() in SENSITIVE_PARAMS else v
        for k, v in params.items()
    }


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with correlation IDs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details with correlation ID."""
        # Generate or extract correlation ID (validate UUID format)
        client_id = request.headers.get("X-Correlation-ID", "")
        correlation_id = client_id if _UUID_RE.match(client_id) else str(uuid.uuid4())

        # Bind context for this request
        clear_contextvars()
        bind_contextvars(
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        # Log request
        start_time = time.time()
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=_sanitize_params(dict(request.query_params)),
        )

        # Process request
        try:
            response = await call_next(request)

            # Use route template for metrics to avoid high-cardinality labels
            route = request.scope.get("route")
            path_template = route.path if route else request.url.path

            # Log response (raw path for debugging)
            duration_ms = (time.time() - start_time) * 1000
            duration_seconds = duration_ms / 1000
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            # Track metrics with route template
            increment_http_requests(
                method=request.method,
                endpoint=path_template,
                status_code=response.status_code,
            )
            observe_http_duration(
                method=request.method,
                endpoint=path_template,
                duration=duration_seconds,
            )

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except Exception as exc:
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            logger.exception(
                "request_failed",
                exc_type=type(exc).__name__,
                duration_ms=duration_ms,
            )
            raise

        finally:
            clear_contextvars()
