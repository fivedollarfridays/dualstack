# Configuration Reference

Central reference for all environment variables across DualStack's backend,
frontend, and monitoring stacks.

---

## Quick Start for Local Development

Minimum variables needed to run locally (all others have safe defaults):

| Variable | File | Value |
|----------|------|-------|
| `TURSO_DATABASE_URL` | `backend/.env` | `file:local.db` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `frontend/.env.local` | `pk_test_...` (from Clerk dashboard) |
| `NEXT_PUBLIC_API_URL` | `frontend/.env.local` | `http://localhost:8000` |
| `GRAFANA_ADMIN_PASSWORD` | shell env | Any password for local Grafana |

Everything else is optional for local development. Copy the templates:

```bash
make setup   # or manually:
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

---

## Backend

Source: `backend/.env` (loaded by Pydantic Settings)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | Both | `development` | `development` or `production`. Controls auth bypass, log format, and security behavior. |
| `DATABASE_URL` | Production | `""` | Primary database URL. Takes priority over Turso. Use `postgresql+asyncpg://user:pass@host:5432/db` for production. |
| `TURSO_DATABASE_URL` | Development | `""` | Turso/SQLite database URL. Use `file:local.db` for local development. |
| `TURSO_AUTH_TOKEN` | Production (Turso) | `""` | Auth token for remote Turso databases. Not needed for local `file:` URLs. |
| `CLERK_JWKS_URL` | Production | `""` | Clerk JWKS endpoint for JWT validation. **Without this, all `X-User-ID` headers are trusted (dev only).** |
| `STRIPE_SECRET_KEY` | Production | `""` | Stripe secret API key. Must start with `sk_test_` or `sk_live_`. |
| `STRIPE_WEBHOOK_SECRET` | Production | `""` | Stripe webhook signing secret. Must start with `whsec_`. |
| `LOG_LEVEL` | No | `INFO` | Python logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `LOG_FORMAT` | No | `json` | Log output format (`json` or `text`). |
| `METRICS_API_KEY` | Production | `""` | Bearer token for `/metrics` endpoint. Must be >= 16 characters when set. |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated allowed CORS origins. |

---

## Frontend

Source: `frontend/.env.local` (loaded by Next.js)

### Client-Side (exposed to browser)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Both | — | Clerk publishable key. Starts with `pk_test_` (dev) or `pk_live_` (prod). |
| `NEXT_PUBLIC_API_URL` | Both | — | Backend API base URL. `http://localhost:8000` for local dev. |
| `NEXT_PUBLIC_STRIPE_PRO_PRICE_ID` | Production | — | Stripe Price ID for the Pro plan checkout. |

### Server-Side (Next.js server only)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | `development` | Controls frontend behavior (e.g., DevAuthProvider guard). |

### E2E Testing

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `E2E_CLERK_USER_USERNAME` | E2E only | — | Test user username for Playwright E2E tests. Create in Clerk dashboard. |
| `E2E_CLERK_USER_PASSWORD` | E2E only | — | Test user password for Playwright E2E tests. |
| `CLERK_SECRET_KEY` | E2E only | — | Clerk secret key for `@clerk/testing` setup. |

---

## Monitoring

Source: shell environment or `.env` file in `monitoring/` directory.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GRAFANA_ADMIN_PASSWORD` | Both | — | Grafana admin login password. **Required** — docker-compose fails without it. |
| `PROMETHEUS_BEARER_TOKEN` | Production | — | Bearer token Prometheus uses to scrape `/metrics`. Must equal `METRICS_API_KEY`. |
| `PROMETHEUS_BASIC_AUTH_PASSWORD` | Production | — | Bcrypt hash for Prometheus UI basic-auth (`web.yml`). Generate with `htpasswd -nBC 10 ""`. |
| `GF_DATASOURCE_PROM_USER` | Production | `admin` | Username Grafana uses for Prometheus basic-auth. |
| `GF_DATASOURCE_PROM_PASSWORD` | Production | — | Plaintext password Grafana uses for Prometheus basic-auth. Must match the password hashed in `PROMETHEUS_BASIC_AUTH_PASSWORD`. |
| `GF_ALERTING_SLACK_WEBHOOK_URL` | Production | placeholder | Slack incoming webhook URL for alert notifications. |
| `GF_ALERTING_PAGERDUTY_KEY` | Optional | — | PagerDuty integration key for critical alert routing. |

---

## Cross-Stack Dependencies

Some variables must be coordinated across stacks to avoid silent failures:

### Clerk Environment Matching

The Clerk key environment (test vs. live) must match across stacks:

- `CLERK_JWKS_URL` (backend) must point to the same Clerk environment as
  `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (frontend)
- Using `pk_test_` with a live JWKS URL (or vice versa) causes **silent auth
  failures** — tokens validate against the wrong key set

### Metrics / Prometheus Auth

- `METRICS_API_KEY` (backend) must equal `PROMETHEUS_BEARER_TOKEN` (monitoring)
- Both protect the `/metrics` endpoint: the backend checks the Bearer token,
  Prometheus sends it when scraping

### Prometheus Basic-Auth Chain

- `PROMETHEUS_BASIC_AUTH_PASSWORD` (bcrypt hash in `web.yml`) must correspond to
  the plaintext password used by `GF_DATASOURCE_PROM_PASSWORD` (Grafana)
- `GF_DATASOURCE_PROM_USER` must match the username in `web.yml` (default: `admin`)

---

## Security Notes

- **Never commit** `.env`, `.env.local`, or any file containing real secrets
- Stripe keys are validated at startup: `sk_test_`/`sk_live_` prefix for secret
  keys, `whsec_` prefix for webhook secrets
- `METRICS_API_KEY` must be >= 16 characters when set (enforced by Pydantic)
- In development, empty `CLERK_JWKS_URL` disables JWT validation — all
  `X-User-ID` headers are trusted. **Never deploy to production without setting
  this.**
- `GRAFANA_ADMIN_PASSWORD` is required even in development — docker-compose
  will refuse to start without it
