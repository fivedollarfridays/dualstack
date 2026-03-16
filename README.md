# DualStack

![Security](https://img.shields.io/badge/security-0_vulnerabilities-brightgreen) ![Tests](https://img.shields.io/badge/tests-1334_passing-brightgreen) ![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen) ![Bundle](https://img.shields.io/badge/bundle-102kB_shared-brightgreen) ![Deploy](https://img.shields.io/badge/deploy-84s-brightgreen) ![Built with PairCoder](https://img.shields.io/badge/built%20with-PairCoder-blueviolet)

Production-ready **FastAPI + Next.js** SaaS starter kit with auth, payments, file uploads, real-time WebSocket, and monitoring out of the box.

## What's Included

- **FastAPI Backend** -- Python 3.13, async SQLAlchemy, Pydantic v2, structured logging, Prometheus metrics
- **Next.js 15 Frontend** -- App Router, TypeScript, Tailwind CSS, shadcn/ui components
- **Authentication** -- Clerk (backend JWT via JWKS + frontend components)
- **Database** -- SQLite (Turso-ready) with Drizzle ORM (frontend) and SQLAlchemy (backend)
- **Payments** -- Stripe Checkout + Customer Portal with plan enforcement
- **File Uploads** -- S3/R2-compatible presigned URLs with content-type allowlisting
- **Real-time** -- WebSocket with JWT authentication and per-user message routing
- **RBAC** -- Role-based access control with admin, user, and custom roles
- **Admin Dashboard** -- User management, health checks, audit logs
- **Monitoring** -- Prometheus + Grafana + Alertmanager (Docker Compose)
- **Health Checks** -- Kubernetes liveness + readiness probes
- **Background Jobs** -- APScheduler for async task scheduling
- **Email** -- Resend integration for transactional email
- **Testing** -- pytest (845 tests, backend) + Jest + Playwright (482 tests, frontend)
- **Generic CRUD Entity** -- "Items" module demonstrating the full pattern to extend

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Frontend | Next.js 15, React 18, TypeScript 5 |
| Database | SQLite (Turso-ready with configuration) |
| ORM | SQLAlchemy (backend), Drizzle (frontend) |
| Auth | Clerk (JWT + JWKS verification) |
| Payments | Stripe (Checkout, Portal, Webhooks) |
| File Storage | S3/R2-compatible (presigned URLs) |
| Email | Resend (transactional templates) |
| Styling | Tailwind CSS, shadcn/ui |
| State | React Query, Zustand |
| Real-time | WebSocket (JWT-authenticated) |
| Monitoring | Prometheus, Grafana, Alertmanager |
| Testing | pytest, Jest, Playwright |
| Deployment | Docker (backend), Vercel (frontend) |

## Project Structure

```
dualstack/
├── backend/                  # FastAPI API (Python 3.13)
│   ├── app/
│   │   ├── core/             # Infrastructure (config, db, errors, logging, metrics)
│   │   │   ├── ws_routes.py  # WebSocket endpoint and routing
│   │   │   ├── ws_auth.py    # WebSocket JWT authentication
│   │   │   └── websocket.py  # Connection manager
│   │   ├── health/           # K8s health probes (liveness + readiness)
│   │   ├── items/            # Generic CRUD entity
│   │   ├── users/            # User profile and account management
│   │   ├── admin/            # Admin dashboard (user mgmt, audit, health)
│   │   ├── billing/          # Stripe integration (checkout, portal, webhooks)
│   │   └── files/            # File upload/download (S3/R2 presigned URLs)
│   ├── tests/                # pytest (845 tests, 95% coverage)
│   ├── alembic/              # DB migrations
│   └── scripts/              # Seed scripts
├── frontend/                 # Next.js 15 (TypeScript)
│   ├── src/
│   │   ├── app/              # Pages (dashboard, items, billing, settings, auth, onboarding)
│   │   ├── components/       # UI components (upload, onboarding, etc.)
│   │   ├── db/               # Drizzle + Turso
│   │   ├── lib/              # API clients, auth, utils
│   │   └── hooks/            # React Query + WebSocket hooks
│   └── drizzle/              # Frontend migrations
└── monitoring/               # Prometheus + Grafana + Alertmanager
    ├── docker-compose.yml
    ├── prometheus/
    ├── grafana/
    └── alertmanager/
```

## Quickstart

See [GETTING_STARTED.md](GETTING_STARTED.md) for a detailed walkthrough.

### Prerequisites

- Python 3.13+
- Node.js 18+
- pnpm (`npm install -g pnpm` or `corepack enable`)
- Docker (for monitoring stack)

### Quick Start (Makefile)

```bash
make setup   # Install deps, create .env files, run migrations
make dev     # Start backend, frontend, and monitoring
```

Edit `backend/.env` and `frontend/.env.local` with your Clerk, Stripe, and database keys.

### Available Make Targets

| Command | Description |
|---------|-------------|
| `make setup` | Install dependencies and create `.env` files from templates |
| `make dev` | Start backend, frontend, and monitoring stack |
| `make test` | Run backend and frontend test suites |
| `make build` | Build Docker images via docker-compose |
| `make clean` | Stop services and remove build artifacts |
| `make help` | Show available targets |

### Manual Setup

<details>
<summary>Step-by-step without Make</summary>

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head

# Frontend
cd ../frontend
pnpm install
cp .env.example .env.local

# Start services (separate terminals)
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && pnpm dev
cd monitoring && docker compose up -d
```

</details>

### pnpm Workspace

DualStack uses a **pnpm workspace** for coordinated dependency management and cross-stack operations from the project root.

```bash
pnpm install       # Install frontend dependencies (workspace-aware)
pnpm dev           # Start backend, frontend, and monitoring concurrently
pnpm test          # Run backend (pytest) and frontend (jest) test suites
pnpm build         # Build frontend for production
pnpm run install:all  # Install both backend (pip) and frontend (pnpm) deps
```

The backend (Python/pip) is not a pnpm workspace package. Python dependencies are managed separately via `pip install -r requirements-dev.txt`.

### Alternative: Docker Compose (full stack)

```bash
docker compose up --build
```

### Open your browser

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Grafana: http://localhost:3001

## API Endpoints

All `/api/v1/*` routes require a `Bearer` token (Clerk JWT) in the `Authorization` header.

### Items

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/items` | JWT | List items (paginated) |
| `POST` | `/api/v1/items` | JWT | Create item |
| `GET` | `/api/v1/items/:id` | JWT | Get item by ID |
| `PATCH` | `/api/v1/items/:id` | JWT | Update item |
| `DELETE` | `/api/v1/items/:id` | JWT | Delete item |

### Users

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/users/me` | JWT | Get current user subscription info |
| `GET` | `/api/v1/users/me/profile` | JWT | Get user profile |
| `PATCH` | `/api/v1/users/me/profile` | JWT | Update user profile |
| `DELETE` | `/api/v1/users/me` | JWT | Delete user account |

### Admin

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/admin/users` | JWT + Admin | List all users |
| `PATCH` | `/api/v1/admin/users/:id/role` | JWT + Admin | Update user role |
| `GET` | `/api/v1/admin/health` | JWT + Admin | System health details |
| `GET` | `/api/v1/admin/audit` | JWT + Admin | View audit log |

### Billing

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/billing/checkout` | JWT | Create Stripe checkout session |
| `POST` | `/api/v1/billing/portal` | JWT | Open Stripe customer portal |
| `POST` | `/webhooks/stripe` | Stripe sig | Stripe webhook receiver |

### Files

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/files/upload-url` | JWT | Generate presigned upload URL |
| `GET` | `/api/v1/files` | JWT | List user files |
| `GET` | `/api/v1/files/:id/download-url` | JWT | Generate presigned download URL |
| `DELETE` | `/api/v1/files/:id` | JWT | Delete file record and object |

### Health and Monitoring

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health/live` | No | Liveness probe (no I/O) |
| `GET` | `/health/ready` | No | Readiness probe (checks DB) |
| `GET` | `/health` | No | Combined health status |
| `GET` | `/metrics` | API key | Prometheus metrics |
| `WS` | `/ws` | JWT | WebSocket (real-time events) |

All error responses use the shape `{ "error": { "code": "...", "message": "..." } }`.

## Plan Tiers

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| Max items | 10 | 1,000 | Unlimited |
| CRUD operations | Yes | Yes | Yes |
| Billing portal | No | Yes | Yes |
| CSV export | No | Yes | Yes |
| All features | No | No | Yes |

Users start on the Free tier. Upgrade via Stripe Checkout. Plan enforcement is handled server-side through the entitlements system.

## Environment Variables

DualStack uses two config files for local development:

- **`backend/.env`** -- Loaded by Pydantic Settings. Contains all backend configuration.
- **`frontend/.env.local`** -- Loaded by Next.js. Contains public + server-side keys.

### Backend Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | `development` | `development` or `production` |
| `DATABASE_URL` | For prod | -- | Async DB URL (e.g. `postgresql+asyncpg://...`) |
| `TURSO_DATABASE_URL` | For dev | -- | Turso/SQLite URL (e.g. `file:local.db`) |
| `TURSO_AUTH_TOKEN` | For Turso | -- | Turso authentication token |
| `CLERK_JWKS_URL` | For prod | -- | Clerk JWKS URL for JWT verification |
| `CLERK_AUDIENCE` | No | -- | Expected JWT `aud` claim (validates when set) |
| `STRIPE_SECRET_KEY` | For billing | -- | Stripe API secret (`sk_test_` or `sk_live_`) |
| `STRIPE_WEBHOOK_SECRET` | For prod | -- | Stripe webhook signing secret (`whsec_`) |
| `RESEND_API_KEY` | For email | -- | Resend API key for transactional email |
| `EMAIL_FROM_ADDRESS` | No | `no-reply@dualstack.app` | Sender email address |
| `EMAIL_FROM_NAME` | No | `DualStack` | Sender display name |
| `STORAGE_BUCKET` | For uploads | -- | S3/R2 bucket name |
| `STORAGE_ACCESS_KEY` | For uploads | -- | S3/R2 access key ID |
| `STORAGE_SECRET_KEY` | For uploads | -- | S3/R2 secret access key |
| `STORAGE_ENDPOINT` | For R2 | -- | S3-compatible endpoint URL |
| `STORAGE_REGION` | No | `us-east-1` | S3 region |
| `METRICS_API_KEY` | For prod | -- | API key protecting `/metrics` (min 16 chars) |
| `LOG_LEVEL` | No | `INFO` | Python log level |
| `LOG_FORMAT` | No | `json` | Log format (`json` or `text`) |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated allowed origins |
| `FORWARDED_ALLOW_IPS` | For prod | `127.0.0.1` | Trusted proxy IPs for X-Forwarded-For |

### Frontend Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Yes | Clerk frontend key (`pk_test_` or `pk_live_`) |
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL (e.g. `http://localhost:8000`) |
| `NEXT_PUBLIC_STRIPE_PRO_PRICE_ID` | For billing | Stripe price ID for the Pro plan |
| `ENVIRONMENT` | No | `development` or `production` |
| `E2E_CLERK_USER_USERNAME` | For E2E | Clerk test user username (Playwright) |
| `E2E_CLERK_USER_PASSWORD` | For E2E | Clerk test user password (Playwright) |

**Key matching rule:** The Clerk key environment (test/live) must match between frontend (`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`) and backend (`CLERK_JWKS_URL`). Mismatched environments cause silent auth failures.

## Webhook Setup

### Stripe Webhooks

1. Go to [Stripe Dashboard](https://dashboard.stripe.com) > **Developers** > **Webhooks** > **Add Endpoint**
2. Set the URL to `https://YOUR_API_URL/webhooks/stripe`
3. Subscribe to events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
4. Copy the **Signing Secret** and set it as `STRIPE_WEBHOOK_SECRET` in `backend/.env`

**Local testing:**

```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
```

The CLI prints a webhook signing secret -- use that as `STRIPE_WEBHOOK_SECRET` during local dev.

**Test card numbers:**

| Card | Result |
|------|--------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Declined payment |
| `4000 0025 0000 3155` | Requires 3D Secure |

Use any future expiry date, any CVC, and any postal code.

## Running Tests

```bash
# Backend (845 tests)
cd backend
pip install -r requirements-dev.txt
pytest --cov=app --cov-report=term-missing tests/

# Frontend (482 tests)
cd frontend
pnpm test
pnpm run test:coverage

# Both via Make
make test
```

## Security

### Headers

- **CSP** with nonces for inline scripts (`script-src 'nonce-...'`)
- **HSTS** with `max-age` and `includeSubDomains`
- **X-Frame-Options**: `DENY`
- **X-Content-Type-Options**: `nosniff`
- **Referrer-Policy**: strict origin

### Rate Limiting

All endpoints are rate-limited via SlowAPI. Health endpoints use `120/minute`. The `/metrics` endpoint requires an API key (`METRICS_API_KEY`).

### Input Validation

- All request bodies validated with Pydantic v2 schemas
- File upload `content_type` restricted to an allowlist (blocks `text/html`, `image/svg+xml`, `application/javascript`, `application/octet-stream`)
- Filenames sanitized to strip path traversal (`../../etc/passwd` becomes `passwd`)
- User profile `display_name` strips `<` and `>` characters to prevent stored XSS
- User profile `avatar_url` rejects non-HTTPS schemes

### Authentication

- JWT verification via Clerk JWKS endpoint
- WebSocket connections authenticated with JWT
- JWT `aud` claim validated when `CLERK_AUDIENCE` is configured
- Dev mode accepts `X-User-ID` header (blocked in production)

### Authorization

- RBAC with role-based route protection (`admin`, `user`)
- Feature entitlements enforced per plan tier
- Admin routes require admin role
- WebSocket events scoped to owning user (no broadcast)

### Audit Logging

All sensitive operations (user changes, billing events, file operations, admin actions) are persisted to the audit log table and queryable via the admin API.

## Operations

### Health Checks

DualStack exposes Kubernetes-compatible probes:

- **Liveness** (`GET /health/live`) -- returns immediately, no I/O. Use for container restart decisions.
- **Readiness** (`GET /health/ready`) -- checks database connectivity. Use for traffic routing decisions.
- **Combined** (`GET /health`) -- full status with component breakdown.

### Prometheus Metrics

Metrics are exposed at `GET /metrics` in Prometheus exposition format. In production, this endpoint is protected by `METRICS_API_KEY`.

Configure your Prometheus scrape config:

```yaml
scrape_configs:
  - job_name: dualstack-api
    scheme: https
    authorization:
      credentials: YOUR_METRICS_API_KEY
    static_configs:
      - targets: ['your-api-host:443']
```

### Monitoring Stack

The `monitoring/` directory includes a Docker Compose stack with:

- **Prometheus** -- metrics collection and alerting rules
- **Grafana** -- dashboards and visualization (port 3001)
- **Alertmanager** -- alert routing and notification

Start it with:

```bash
cd monitoring && docker compose up -d
```

### Backup and Restore

For Turso/SQLite deployments, back up the database file directly. For PostgreSQL, use standard `pg_dump`/`pg_restore`. The `scripts/` directory includes helper scripts for database operations.

## Deployment

### Backend (Docker / Render)

```bash
cd backend
docker build -t dualstack-api .
docker run -p 8000:8000 --env-file .env dualstack-api
```

Or deploy to Render using the included [`render.yaml`](render.yaml).

### Frontend (Vercel)

```bash
cd frontend
vercel
```

Set environment variables in the Vercel dashboard:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `NEXT_PUBLIC_API_URL` (your deployed backend URL)
- `NEXT_PUBLIC_STRIPE_PRO_PRICE_ID`

## Customization

### Replacing "Items" with your domain entity

Run the rename script to automatically update all files, directories, imports, and references:

```bash
python scripts/rename.py --from item --to project
```

Preview changes first with `--dry-run`:

```bash
python scripts/rename.py --from item --to project --dry-run
```

For irregular plurals, use the override flags:

```bash
python scripts/rename.py --from item --to person --to-plural people
```

The script handles class names, variable names, route prefixes, import paths, file renames, and directory renames across the entire codebase.

### Adding new API routes

1. Create `app/your_module/routes.py` with a FastAPI `APIRouter`
2. Add model and schemas in `app/your_module/models.py` and `schemas.py`
3. Add service layer in `app/your_module/service.py`
4. Register the router in `app/main.py`:
   ```python
   from app.your_module.routes import router as your_module_router
   app.include_router(your_module_router, prefix="/api/v1")
   ```
5. Create an Alembic migration: `alembic revision --autogenerate -m "add your_module"`
6. Write tests in `tests/your_module/`

### Adding sidebar navigation

Edit `frontend/src/app/(dashboard)/layout.tsx` and add an entry to the `navItems` array:

```typescript
const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/items', label: 'Items' },
  { href: '/your-page', label: 'Your Page' },  // add here
  { href: '/billing', label: 'Billing' },
  { href: '/settings', label: 'Settings' },
];
```

### Customizing billing plans

1. Update the price ID in `frontend/.env.local` (`NEXT_PUBLIC_STRIPE_PRO_PRICE_ID`)
2. Edit `frontend/src/app/(dashboard)/billing/page.tsx` to match your plan names and pricing
3. Modify `backend/app/billing/plans.py` to adjust tier limits and features

## Built With

This project was built using [PairCoder](https://github.com/bpsai-labs/paircoder) -- an AI-augmented pair programming framework for sprint-based development with enforcement gates, typed memory, and Trello integration.

## License

Personal Use License - Copyright (c) 2026 Kevin Masterson. See [LICENSE](LICENSE) for details.
