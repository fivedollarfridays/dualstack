# Security

This document describes the security controls implemented in DualStack. Every claim is verifiable in the referenced source files.

## Content Security Policy (CSP)

**Backend** (`backend/app/core/security_headers.py`): Applies a restrictive CSP to all non-JSON responses: `default-src 'self'; script-src 'none'; style-src 'none'; frame-ancestors 'none'; form-action 'none'`. JSON API responses omit CSP since browsers do not render them. Additional headers include HSTS (1 year, includeSubDomains, preload), X-Frame-Options DENY, X-Content-Type-Options nosniff, and a restrictive Permissions-Policy.

**Frontend** (`frontend/src/lib/csp.ts`): Uses per-request cryptographic nonces for `script-src` and `style-src`. No `unsafe-inline` or `unsafe-eval` directives. Whitelisted origins: `*.clerk.accounts.dev` (auth), `api.stripe.com` (payments), `js.stripe.com` (iframe). Uses `strict-dynamic` for script loading.

## Authentication

**HTTP** (`backend/app/core/auth.py`): Bearer JWTs are verified against the Clerk JWKS endpoint using `fastapi-clerk-auth`. The `sub` claim is extracted as the user ID. JWKS clients are cached in a bounded LRU cache (max 10 entries).

**WebSocket** (`backend/app/core/ws_auth.py`): JWTs are verified via `PyJWKClient` with RS256 signature validation. When `clerk_audience` is configured, the `aud` claim is validated; otherwise audience verification is skipped (dev mode only).

**Dev mode**: When `CLERK_JWKS_URL` is unset, the `X-User-ID` header (HTTP) or `user_id` query param (WebSocket) is trusted. This path is blocked in production: if `environment == "production"` and no JWKS URL is set, requests are rejected with an error.

## Authorization

**RBAC** (`backend/app/core/rbac.py`): Two roles exist: `admin` (level 2) and `member` (level 1). Admin is a superset of member permissions. The `require_role(Role.ADMIN)` dependency enforces minimum role level on admin-only routes. `require_permission()` checks specific permissions against role permission sets.

**Data isolation**: All CRUD endpoints (items, files, users) scope queries by `user_id` to prevent cross-user data access. File list, download, and delete operations all include a `WHERE user_id = :user_id` clause (`backend/app/files/service.py`).

**Last-admin protection** (`backend/app/admin/service.py`): Role changes check admin count before demoting the last admin.

## Input Validation

All API inputs use Pydantic v2 schemas with strict field constraints:

- **Avatar URL** (`backend/app/users/schemas.py`): HTTPS-only scheme validation. Rejects `javascript:`, `data:`, `http://`, and `ftp:` schemes.
- **Display name** (`backend/app/users/schemas.py`): Strips `<` and `>` characters to prevent stored XSS.
- **File content type** (`backend/app/files/schemas.py`): Allowlist of 8 MIME types: `image/png`, `image/jpeg`, `image/gif`, `image/webp`, `application/pdf`, `text/plain`, `text/csv`, `application/json`. Blocks `text/html`, `image/svg+xml`, and `application/javascript`.
- **Filename** (`backend/app/files/service.py`): `PurePosixPath(filename).name` strips path traversal components (e.g., `../../etc/passwd` becomes `passwd`).
- **Search queries** (`backend/app/admin/service.py`): SQL LIKE metacharacters (`\`, `%`, `_`) are escaped before interpolation into ILIKE patterns.

## Rate Limiting

Per-endpoint rate limits via slowapi (`backend/app/core/rate_limit.py`):

| Tier | Limit | Endpoints |
|------|-------|-----------|
| Health | 120/min | `/health`, `/health/ready` |
| Reads | 60/min | GET items, users, files, admin, webhooks |
| Writes | 30/min | POST/PUT/DELETE items, files, profile updates |
| Billing | 10/min | Checkout, portal, role changes |
| Destructive | 3/min | Account deletion |

Client IP is extracted from the `X-Forwarded-For` header. The `forwarded_allow_ips` setting (`backend/app/core/config.py`) must be configured to the reverse proxy IP in production.

## Webhook Security

**Stripe** (`backend/app/billing/service.py`): Webhook payloads are verified using `stripe.Webhook.construct_event` with the `stripe_webhook_secret`. Invalid signatures raise `AuthenticationError` and are logged as audit events with outcome `failure`. The webhook secret is validated at startup to require the `whsec_` prefix (`backend/app/core/config.py`). If the webhook secret is not configured, the endpoint returns `503 Service Unavailable` rather than processing unverified payloads.

## File Upload Security

Implemented in `backend/app/files/service.py` and `backend/app/files/schemas.py`:

- **Direct-to-S3 presigned URLs**: Files are uploaded directly to object storage. The server never proxies file content.
- **Content type restriction**: Only 8 safe MIME types are accepted (no HTML, SVG, or JS).
- **Filename sanitization**: `PurePosixPath.name` strips directory traversal components.
- **Size limit**: 100 MB maximum (`MAX_FILE_SIZE = 100 * 1024 * 1024`).
- **Storage key not exposed**: The `storage_key` field is excluded from API response schemas.
- **Request body limit**: 1 MB maximum for API requests enforced by `ContentSizeLimitMiddleware` (`backend/app/core/security_headers.py`).

## Audit Logging

All write operations are logged via `persist_audit_event` (`backend/app/core/audit.py`), which writes to the `audit_logs` database table and emits a structured log entry. Fields recorded: `user_id`, `action`, `resource_type`, `resource_id`, `outcome`, `detail`, `timestamp`.

Admin users can query audit logs via `GET /api/v1/admin/audit` (`backend/app/admin/routes.py`), protected by `require_role(Role.ADMIN)`.

## Environment Validation

Configuration is managed via `pydantic-settings` (`backend/app/core/config.py`):

- `environment` is restricted to `Literal["development", "production"]`.
- `stripe_secret_key` must start with `sk_test_` or `sk_live_`.
- `stripe_webhook_secret` must start with `whsec_`.
- `metrics_api_key` must be at least 16 characters when set.
- CORS origins are parsed from a comma-separated allowlist, not wildcarded.

## Cookie Security

The API is stateless and issues no cookies. Session management is delegated to Clerk on the frontend. All authentication uses Bearer tokens in the Authorization header.

## WebSocket Security

Implemented in `backend/app/core/ws_auth.py` and `backend/app/core/websocket.py`:

- **JWKS-validated JWT**: RS256 signature verification via `PyJWKClient`.
- **Audience validation**: `aud` claim checked when `clerk_audience` is configured.
- **Per-user event routing**: `ConnectionManager.send_to_user()` sends events only to the authenticated user's connections. No broadcast capability exists (removed by design).
- **Connection tracking**: Broken connections are automatically cleaned up during send operations.
