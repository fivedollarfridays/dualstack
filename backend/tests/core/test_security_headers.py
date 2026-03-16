"""Tests for security headers middleware."""

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI, Request

from app.core.security_headers import (
    ContentSizeLimitMiddleware,
    SecurityHeadersMiddleware,
    MAX_BODY_SIZE,
)


@pytest.fixture
def app_with_headers():
    """Create a test app with security headers middleware."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/test")
    async def test_route():
        return {"ok": True}

    return app


class TestSecurityHeadersMiddleware:
    async def test_x_content_type_options(self, app_with_headers):
        transport = ASGITransport(app=app_with_headers)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/test")
            assert r.headers["x-content-type-options"] == "nosniff"

    async def test_x_frame_options(self, app_with_headers):
        transport = ASGITransport(app=app_with_headers)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/test")
            assert r.headers["x-frame-options"] == "DENY"

    async def test_referrer_policy(self, app_with_headers):
        transport = ASGITransport(app=app_with_headers)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/test")
            assert r.headers["referrer-policy"] == "strict-origin-when-cross-origin"

    async def test_permissions_policy(self, app_with_headers):
        transport = ASGITransport(app=app_with_headers)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/test")
            assert (
                r.headers["permissions-policy"]
                == "camera=(), microphone=(), geolocation=()"
            )

    async def test_content_security_policy_on_non_json(self):
        """SEC-007: CSP header must be present on non-JSON responses."""
        from starlette.responses import HTMLResponse

        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/page")
        async def page_route():
            return HTMLResponse("<html><body>hello</body></html>")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/page")
            assert "content-security-policy" in r.headers
            assert "default-src" in r.headers["content-security-policy"]

    async def test_strict_transport_security(self, app_with_headers):
        """SEC-007: HSTS header must be present with preload."""
        transport = ASGITransport(app=app_with_headers)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/test")
            hsts = r.headers["strict-transport-security"]
            assert "max-age" in hsts
            assert "preload" in hsts

    async def test_no_csp_on_json_responses(self, app_with_headers):
        """AUDIT-012: JSON API responses should not include CSP header."""
        transport = ASGITransport(app=app_with_headers)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/test")
            assert "content-security-policy" not in r.headers

    async def test_csp_on_html_responses(self):
        """AUDIT-012: HTML responses should still include CSP header."""
        from starlette.responses import HTMLResponse

        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/html")
        async def html_route():
            return HTMLResponse("<html><body>hello</body></html>")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/html")
            assert "content-security-policy" in r.headers

    async def test_csp_contains_script_src_none(self):
        """T19.5: CSP must block inline scripts with script-src 'none'."""
        from starlette.responses import HTMLResponse

        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/page")
        async def page_route():
            return HTMLResponse("<html></html>")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/page")
            csp = r.headers["content-security-policy"]
            assert "script-src 'none'" in csp
            assert "frame-ancestors 'none'" in csp
            assert "form-action 'none'" in csp


@pytest.fixture
def app_with_size_limit():
    """Create a test app with content size limit middleware."""
    app = FastAPI()
    app.add_middleware(ContentSizeLimitMiddleware)

    @app.post("/upload")
    async def upload_route(request: Request):
        body = await request.body()
        return {"size": len(body)}

    @app.get("/health")
    async def health_route():
        return {"ok": True}

    return app


class TestContentSizeLimitMiddleware:
    """Tests for ContentSizeLimitMiddleware including chunked transfer encoding."""

    async def test_content_length_within_limit(self, app_with_size_limit):
        """Requests with Content-Length within limit pass through."""
        transport = ASGITransport(app=app_with_size_limit)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.post("/upload", content=b"hello")
            assert r.status_code == 200
            assert r.json()["size"] == 5

    async def test_content_length_exceeds_limit(self, app_with_size_limit):
        """Requests with Content-Length exceeding limit return 413."""
        transport = ASGITransport(app=app_with_size_limit)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.post(
                "/upload",
                content=b"x",
                headers={"content-length": str(MAX_BODY_SIZE + 1)},
            )
            assert r.status_code == 413
            assert r.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"

    async def test_invalid_content_length(self, app_with_size_limit):
        """Requests with invalid Content-Length return 400."""
        transport = ASGITransport(app=app_with_size_limit)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.post(
                "/upload",
                content=b"hello",
                headers={"content-length": "not-a-number"},
            )
            assert r.status_code == 400
            assert r.json()["error"]["code"] == "BAD_REQUEST"

    async def test_no_content_length_small_body_passes(self, app_with_size_limit):
        """Requests without Content-Length but small body pass through."""
        body_received = {}

        async def receive():
            return {
                "type": "http.request",
                "body": b"small payload",
                "more_body": False,
            }

        async def send(message):
            if message["type"] == "http.response.start":
                body_received["status"] = message["status"]

        scope = {
            "type": "http",
            "method": "POST",
            "path": "/upload",
            "query_string": b"",
            "root_path": "",
            "headers": [],  # No content-length header
            "app_state": {},
        }

        await app_with_size_limit(scope, receive, send)
        assert body_received["status"] == 200

    async def test_no_content_length_large_body_rejected(self, app_with_size_limit):
        """NEW-007: Requests without Content-Length but oversized body return 413."""
        response_status = {}
        response_body = b""
        oversized = b"x" * (MAX_BODY_SIZE + 1)
        sent = False

        async def receive():
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": oversized, "more_body": False}
            return {"type": "http.disconnect"}

        async def send(message):
            nonlocal response_body
            if message["type"] == "http.response.start":
                response_status["status"] = message["status"]
            elif message["type"] == "http.response.body":
                response_body += message.get("body", b"")

        scope = {
            "type": "http",
            "method": "POST",
            "path": "/upload",
            "query_string": b"",
            "root_path": "",
            "headers": [],  # No content-length — simulates chunked transfer
            "app_state": {},
        }

        await app_with_size_limit(scope, receive, send)
        assert response_status["status"] == 413

    async def test_get_requests_unaffected(self, app_with_size_limit):
        """GET requests without body are not affected."""
        transport = ASGITransport(app=app_with_size_limit)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.get("/health")
            assert r.status_code == 200

    async def test_exact_limit_passes(self, app_with_size_limit):
        """Request body exactly at the limit passes."""
        transport = ASGITransport(app=app_with_size_limit)
        exact_body = b"x" * MAX_BODY_SIZE
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.post("/upload", content=exact_body)
            assert r.status_code == 200

    async def test_one_byte_over_limit_rejected(self, app_with_size_limit):
        """Request body one byte over the limit is rejected."""
        transport = ASGITransport(app=app_with_size_limit)
        over_body = b"x" * (MAX_BODY_SIZE + 1)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            r = await c.post("/upload", content=over_body)
            assert r.status_code == 413

    async def test_no_double_response_start_when_app_already_responded(self):
        """If the app has already sent response.start, middleware must not send another."""
        from app.core.security_headers import ContentSizeLimitMiddleware

        response_starts = 0
        oversized = b"x" * (MAX_BODY_SIZE + 1)
        chunk_index = 0
        chunks = [oversized[:1024], oversized[1024:]]  # Split into two chunks

        # App that starts responding before fully consuming the body
        async def eager_app(scope, receive, send):
            # Start response before reading body
            await send({"type": "http.response.start", "status": 200, "headers": []})
            # Now try to read body — this will trigger the size limit
            await receive()
            _ = await receive()  # Second chunk exceeds limit
            await send({"type": "http.response.body", "body": b"ok"})

        middleware = ContentSizeLimitMiddleware(eager_app)

        async def receive():
            nonlocal chunk_index
            if chunk_index < len(chunks):
                chunk = chunks[chunk_index]
                chunk_index += 1
                return {
                    "type": "http.request",
                    "body": chunk,
                    "more_body": chunk_index < len(chunks),
                }
            return {"type": "http.disconnect"}

        async def send(message):
            nonlocal response_starts
            if message.get("type") == "http.response.start":
                response_starts += 1

        scope = {
            "type": "http",
            "method": "POST",
            "path": "/upload",
            "query_string": b"",
            "root_path": "",
            "headers": [],
            "app_state": {},
        }

        await middleware(scope, receive, send)
        # Must NOT have sent a second response.start (would crash Uvicorn)
        assert response_starts == 1
