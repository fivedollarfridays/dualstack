"""Security headers and request protection middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
}

CSP_HEADER = "default-src 'self'"


MAX_BODY_SIZE = 1 * 1024 * 1024  # 1 MB


class ContentSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with bodies exceeding MAX_BODY_SIZE."""

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > MAX_BODY_SIZE:
                    return JSONResponse(
                        status_code=413,
                        content={"error": {"code": "PAYLOAD_TOO_LARGE", "message": "Request body too large"}},
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"error": {"code": "BAD_REQUEST", "message": "Invalid Content-Length"}},
                )
        return await call_next(request)


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
