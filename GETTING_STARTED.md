# Getting Started with DualStack

This guide walks you through setting up DualStack for your own SaaS product. By the end, you'll have a working app with authentication, billing, file uploads, and a dashboard.

## What You're Getting

DualStack is a full-stack SaaS starter with two main components:

```
backend/     -- FastAPI API (Python 3.13, SQLAlchemy, Pydantic v2)
frontend/    -- Next.js 15 frontend (App Router, TypeScript, Tailwind)
monitoring/  -- Prometheus + Grafana + Alertmanager (Docker Compose)
```

Clerk handles auth. Stripe handles billing. S3/R2 handles file uploads. SQLite (Turso-ready) or PostgreSQL stores your data. The API validates everything with Pydantic schemas, and the frontend uses React Query for data fetching with WebSocket for real-time updates.

## Prerequisites

Before starting, make sure you have:

- **Python 3.13+** -- [python.org](https://www.python.org/downloads/)
- **Node.js 18+** -- [nodejs.org](https://nodejs.org)
- **pnpm** -- `npm install -g pnpm` or `corepack enable`
- **Docker** -- [docker.com](https://www.docker.com/get-started) (for monitoring stack, optional for dev)

You will also need accounts on:

- **Clerk** (auth) -- [dashboard.clerk.com](https://dashboard.clerk.com) (free tier works)
- **Stripe** (billing) -- [dashboard.stripe.com](https://dashboard.stripe.com/register) (test mode)

These are optional until you need their features:

- **Resend** (email) -- [resend.com](https://resend.com)
- **Cloudflare R2** or **AWS S3** (file storage)

## Step 1: Clone and Install

```bash
git clone <your-repo-url>
cd dualstack
```

### Option A: Makefile (recommended)

```bash
make setup
```

This installs backend and frontend dependencies, copies `.env.example` files, and runs database migrations.

### Option B: Manual

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# Frontend
cd ../frontend
pnpm install
```

## Step 2: Configure Environment

Copy the example files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

### Minimum Config (just auth)

To see the dashboard running, you only need Clerk keys.

**`backend/.env`** -- set these:

```
ENVIRONMENT=development
TURSO_DATABASE_URL=file:local.db
CLERK_JWKS_URL=https://your-clerk-instance.clerk.accounts.dev/.well-known/jwks.json
```

**`frontend/.env.local`** -- set these:

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Billing, file uploads, and email are disabled until you add their keys. The API logs warnings for missing optional config on startup.

### Where to Get Your Keys

**Clerk:**

1. Create an application at [dashboard.clerk.com](https://dashboard.clerk.com)
2. Go to **API Keys** -- copy the Publishable Key and JWKS URL
3. The JWKS URL looks like `https://your-instance.clerk.accounts.dev/.well-known/jwks.json`

**Stripe:**

1. Use test mode at [dashboard.stripe.com](https://dashboard.stripe.com)
2. Go to **Developers** > **API keys** -- copy the Secret Key (`sk_test_...`)
3. Create a product with a monthly price -- copy the Price ID (`price_...`)

**Key matching rule:** The Clerk key environment must match between frontend and backend. Using `pk_test_` with a live JWKS URL (or vice versa) causes silent auth failures.

### Full Config

Once you're ready for all features, add the remaining variables:

```
# backend/.env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
RESEND_API_KEY=re_...
STORAGE_BUCKET=your-bucket-name
STORAGE_ACCESS_KEY=your-access-key
STORAGE_SECRET_KEY=your-secret-key
STORAGE_ENDPOINT=https://your-account.r2.cloudflarestorage.com
METRICS_API_KEY=your-metrics-key-min-16-chars
```

```
# frontend/.env.local
NEXT_PUBLIC_STRIPE_PRO_PRICE_ID=price_...
```

See the [Environment Variables table in README.md](README.md#environment-variables) for the complete reference.

## Step 3: Set Up the Database

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

This creates all tables in your local SQLite database. For production, set `DATABASE_URL` to a PostgreSQL connection string (`postgresql+asyncpg://...`).

### Seed Demo Data

```bash
make seed
```

Or manually:

```bash
cd backend
python -m scripts.seed
```

This inserts a demo user and sample items so you have data to work with immediately.

## Step 4: Start Development

### Option A: Makefile

```bash
make dev
```

This starts the backend, frontend, and monitoring stack concurrently.

### Option B: pnpm Workspace

```bash
pnpm dev
```

### Option C: Manual (separate terminals)

```bash
# Terminal 1 -- Backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 -- Frontend
cd frontend
pnpm dev

# Terminal 3 -- Monitoring (optional)
cd monitoring
docker compose up -d
```

## Step 5: Verify Everything Works

Open these URLs in your browser:

| URL | What You Should See |
|-----|---------------------|
| http://localhost:3000 | Next.js frontend with Clerk sign-in |
| http://localhost:8000 | `{"message": "DualStack API", "status": "running"}` |
| http://localhost:8000/docs | Swagger UI with all API endpoints |
| http://localhost:8000/health/live | `{"status": "ok"}` |
| http://localhost:8000/health/ready | `{"status": "ok", "database": "ok"}` |
| http://localhost:3001 | Grafana dashboard (if monitoring is running) |

### Smoke Test from the Command Line

```bash
# Health check
curl http://localhost:8000/health/live

# List items (requires auth -- expect 401 without a token)
curl http://localhost:8000/api/v1/items
```

In development mode (without `CLERK_JWKS_URL`), you can pass a user ID directly:

```bash
curl -H "X-User-ID: test-user-1" http://localhost:8000/api/v1/items
```

This header is blocked in production.

## Step 6: What to Do Next

Now that everything is running, here's what to try:

### Create Items

Sign in through Clerk at http://localhost:3000, then create items from the dashboard. The API enforces plan limits -- free users can create up to 10 items.

### Test Billing

1. Set `STRIPE_SECRET_KEY` and `NEXT_PUBLIC_STRIPE_PRO_PRICE_ID` in your env files
2. Click "Upgrade" in the billing page
3. Use test card `4242 4242 4242 4242` with any future expiry and CVC
4. After checkout, your plan upgrades and item limits increase

For local webhook testing:

```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
```

Copy the webhook signing secret it prints and set it as `STRIPE_WEBHOOK_SECRET`.

### Test File Uploads

1. Set the storage variables (`STORAGE_BUCKET`, `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY`, `STORAGE_ENDPOINT`)
2. Upload a file through the API -- the system generates presigned URLs for direct client-to-storage uploads
3. Content types are restricted to a safe allowlist (no HTML, SVG, or JavaScript files)

### Customize the Entity

DualStack ships with a generic "Items" entity. To rename it to your domain (e.g., "projects", "posts"):

```bash
python scripts/rename.py --from item --to project
```

Preview first with `--dry-run`, or use `--to-plural` for irregular plurals. See `python scripts/rename.py --help` for details.

### Set Up Monitoring

```bash
cd monitoring
docker compose up -d
```

Open Grafana at http://localhost:3001 (default credentials: admin/admin). Prometheus scrapes the API's `/metrics` endpoint automatically.

## Troubleshooting

**Backend won't start -- "STRIPE_WEBHOOK_SECRET must be set"**

This only happens when `ENVIRONMENT=production`. For local development, make sure `ENVIRONMENT=development` in `backend/.env`.

**Frontend shows blank page after sign-in**

Check that `NEXT_PUBLIC_API_URL` in `frontend/.env.local` points to the running backend (`http://localhost:8000`). Also verify Clerk key environments match (both test or both live).

**"X-User-ID header rejected in production"**

Set `CLERK_JWKS_URL` in `backend/.env`. Without it, the API runs in dev mode and trusts the `X-User-ID` header. In production, JWTs are verified against Clerk's JWKS endpoint.

**Database migration fails**

Make sure you're in the backend directory with the virtual environment activated:

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

If the database file is corrupted, delete `local.db` and run migrations again.

**Stripe webhook events not arriving locally**

Install the Stripe CLI and run:

```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
```

The CLI prints a webhook signing secret. Set it as `STRIPE_WEBHOOK_SECRET` in `backend/.env` and restart the backend.

**Port already in use**

The backend defaults to port 8000 and the frontend to port 3000. Kill existing processes:

```bash
lsof -ti:8000 | xargs kill -9    # Free port 8000
lsof -ti:3000 | xargs kill -9    # Free port 3000
```

**Tests fail with import errors**

Make sure you installed dev dependencies:

```bash
cd backend
pip install -r requirements-dev.txt
```

**Storage/upload features not working**

The API logs a warning on startup when storage is not configured. Set all four storage variables: `STORAGE_BUCKET`, `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY`, and `STORAGE_ENDPOINT`.

## Project Layout Reference

| Directory | Purpose |
|-----------|---------|
| `backend/app/items/` | Generic CRUD entity -- copy this for new entities |
| `backend/app/users/` | User profile and account management |
| `backend/app/admin/` | Admin dashboard routes |
| `backend/app/billing/` | Stripe checkout, portal, and webhooks |
| `backend/app/files/` | File upload/download with presigned URLs |
| `backend/app/health/` | Kubernetes liveness and readiness probes |
| `backend/app/core/` | Config, database, errors, logging, middleware, metrics, RBAC, WebSocket |
| `backend/tests/` | pytest test suite (845 tests) |
| `backend/alembic/` | Database migrations |
| `frontend/src/app/` | Next.js pages and layouts |
| `frontend/src/components/` | React components (UI, upload, onboarding) |
| `frontend/src/hooks/` | React Query hooks, WebSocket hook |
| `frontend/src/lib/` | API client, auth helpers, utilities |
| `monitoring/` | Prometheus + Grafana + Alertmanager Docker Compose stack |

---

Built with [PairCoder](https://github.com/bpsai-labs/paircoder) -- AI-augmented pair programming by BPS AI.
