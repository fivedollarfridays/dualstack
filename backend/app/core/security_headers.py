"""Security headers and request protection middleware."""

import json

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
}

CSP_HEADER = "default-src 'self'; script-src 'none'; style-src 'none'; frame-ancestors 'none'; form-action 'none'"


MAX_BODY_SIZE = 1 * 1024 * 1024  # 1 MB

_413_BODY = json.dumps(
    {"error": {"code": "PAYLOAD_TOO_LARGE", "message": "Request body too large"}}
).encode()
_400_BODY = json.dumps(
    {"error": {"code": "BAD_REQUEST", "message": "Invalid Content-Length"}}
).encode()


class ContentSizeLimitMiddleware:
    """Reject requests with bodies exceeding MAX_BODY_SIZE.

    Enforces limits via both Content-Length header (fast path) and
    streaming byte counting (catches chunked transfer encoding).
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Fast path: check Content-Length header via linear scan (avoids dict allocation)
        content_length_raw = None
        for name, value in scope.get("headers", []):
            if name == b"content-length":
                content_length_raw = value
                break

        if content_length_raw is not None:
            try:
                if int(content_length_raw) > MAX_BODY_SIZE:
                    await self._send_error(send, 413, _413_BODY)
                    return
            except ValueError:
                await self._send_error(send, 400, _400_BODY)
                return

        # Streaming path: wrap receive to count bytes, wrap send to track response state
        bytes_received = 0
        response_started = False

        async def counting_receive() -> dict:
            nonlocal bytes_received
            message = await receive()
            if message.get("type") == "http.request":
                chunk = message.get("body", b"")
                bytes_received += len(chunk)
                if bytes_received > MAX_BODY_SIZE:
                    raise _BodyTooLargeError()
            return message

        async def tracking_send(message: dict) -> None:
            nonlocal response_started
            if message.get("type") == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, counting_receive, tracking_send)
        except _BodyTooLargeError:
            if not response_started:
                await self._send_error(send, 413, _413_BODY)

    @staticmethod
    async def _send_error(send: Send, status: int, body: bytes) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [[b"content-type", b"application/json"]],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )


class _BodyTooLargeError(Exception):
    """Internal signal that body size exceeded the limit."""


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            response.headers["Content-Security-Policy"] = CSP_HEADER
        return response
