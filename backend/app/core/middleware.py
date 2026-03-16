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
from app.core.rate_limit import get_client_ip

logger = get_logger(__name__)

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

SENSITIVE_PARAMS = {
    "token",
    "key",
    "secret",
    "password",
    "api_key",
    "access_token",
    "auth",
    "authorization",
    "apikey",
    "code",
    "state",
    "client_secret",
    "private_key",
    "credential",
}


def _sanitize_params(params: dict) -> dict:
    """Redact sensitive query parameters for safe logging.

    Args:
        params: Dictionary of query parameter key-value pairs.

    Returns:
        Copy with sensitive values replaced by '***'.
    """
    return {k: "***" if k.lower() in SENSITIVE_PARAMS else v for k, v in params.items()}


def _bind_request_context(request: Request) -> str:
    """Bind structlog context vars and return the correlation ID."""
    client_id = request.headers.get("X-Correlation-ID", "")
    correlation_id = client_id if _UUID_RE.match(client_id) else str(uuid.uuid4())
    clear_contextvars()
    bind_contextvars(
        correlation_id=correlation_id,
        method=request.method,
        path=request.url.path,
        client_ip=get_client_ip(request),
    )
    return correlation_id


def _record_request_metrics(
    request: Request, response: Response, duration_seconds: float
) -> None:
    """Record HTTP request metrics using the route template path."""
    route = request.scope.get("route")
    path_template = route.path if route else request.url.path
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


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with correlation IDs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details with correlation ID."""
        correlation_id = _bind_request_context(request)
        start_time = time.time()
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=_sanitize_params(dict(request.query_params)),
        )

        try:
            response = await call_next(request)
            duration_seconds = time.time() - start_time
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=duration_seconds * 1000,
            )
            _record_request_metrics(request, response, duration_seconds)
            response.headers["X-Correlation-ID"] = correlation_id
            return response

        except Exception as exc:
            logger.exception(
                "request_failed",
                exc_type=type(exc).__name__,
                duration_ms=(time.time() - start_time) * 1000,
            )
            raise

        finally:
            clear_contextvars()
