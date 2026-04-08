# DualStack — Contributor Guide

> Full-stack SaaS starter: FastAPI + Next.js 15 + SQLAlchemy + Clerk + Stripe

---

## Project Structure

```
backend/           # FastAPI application (Python 3.13, async SQLAlchemy)
  app/
    core/          # Auth, config, database, rate limiting, metrics, errors
    items/         # Reference CRUD module (models, schemas, routes, service)
    users/         # User profiles and account management
    billing/       # Stripe checkout, portal, webhooks
    files/         # S3/R2 presigned upload/download
    admin/         # Admin endpoints (users, health, audit)
  tests/           # Backend tests (mirrors app/ structure)
frontend/          # Next.js 15 (React, TypeScript, pnpm)
  src/
    app/           # App Router pages (dashboard, items, billing, admin)
    components/    # Shared UI components
    hooks/         # Custom hooks (useItems, useWebSocket, etc.)
    lib/api/       # API client modules
  e2e/             # Playwright end-to-end tests
monitoring/        # Prometheus + Grafana + Alertmanager + Loki (Docker Compose)
scripts/           # Seed data, env checker, rename utility
docs/              # Architecture and operations docs
```

## Adding a New API Endpoint

Follow the Items module pattern in `backend/app/items/`. Each domain module has four files:

| File | Purpose |
|------|---------|
| `models.py` | SQLAlchemy ORM model (inherit from `Base`) |
| `schemas.py` | Pydantic request/response schemas |
| `service.py` | Async business logic functions |
| `routes.py` | FastAPI `APIRouter` with auth, rate limiting, audit logging |

**Steps:**

1. Copy `backend/app/items/` to `backend/app/<yourmodule>/` (or run `python scripts/rename.py --from item --to <yourname>`)
2. Define your model, schemas, service functions, and routes
3. Register the router in `backend/app/main.py`: `app.include_router(router, prefix="/api/v1")`
4. Create an Alembic migration: `alembic revision --autogenerate -m "add <table> table"`
5. Write tests in `backend/tests/<yourmodule>/`

**Key conventions in routes:**
- All routes require JWT auth via `get_current_user_id` dependency
- Rate limiting: `@limiter.limit("60/minute")` for reads, `"30/minute"` for writes
- All mutations log audit events
- User-scoped data access (queries filtered by `user_id`)

## Adding a Frontend Page

Pages use the Next.js App Router in `frontend/src/app/`.

- **Protected pages** go under `(dashboard)/` (requires Clerk auth)
- **Public pages** go at the top level

**Steps:**

1. Create `frontend/src/app/(dashboard)/<yourpage>/page.tsx`
2. Add an API client in `frontend/src/lib/api/<yourmodule>.ts`
3. Create a React Query hook in `frontend/src/hooks/use-<yourmodule>.ts`
4. Add navigation in the sidebar layout (`(dashboard)/layout.tsx`)

**State management:** React Query for server state, Zustand for client state.

## Testing Conventions

### Backend — pytest

```bash
cd backend && pytest --cov=app --cov-report=term-missing tests/
```

- `asyncio_mode = auto` — all async tests run automatically
- Tests mirror the `app/` directory structure
- Use the existing fixtures in `conftest.py` for DB sessions, auth, and test client

### Frontend — Jest

```bash
cd frontend && pnpm test            # run tests
cd frontend && pnpm test:coverage   # with coverage
```

- Test environment: jsdom
- Path alias: `@/` maps to `src/`
- Coverage threshold: 99% (statements, branches, functions, lines)

### End-to-End — Playwright

```bash
cd frontend && pnpm exec playwright test
```

- Auth state stored at `playwright/.clerk/user.json`
- Public tests (landing page) run without auth
- Authenticated tests run with stored Clerk session

### TDD Workflow

Write failing tests first, then implement. For every change:

1. Write a test that fails
2. Write minimal code to make it pass
3. Refactor while keeping tests green

## Architecture Constraints

Keep files small and focused:

| Metric | Source Files | Test Files |
|--------|-------------|------------|
| Max lines (error) | 400 | 600 |
| Max lines (warning) | 200 | 400 |
| Max function length | 50 lines | 50 lines |
| Max functions per file | 15 | 30 |
| Max imports per file | 20 | 40 |

When a file exceeds limits, extract helpers into a separate module.

## Common Commands

```bash
make setup          # Install all dependencies
make dev            # Start backend + frontend dev servers
make test           # Run all tests
make lint           # Run linters (ruff + eslint)
make seed           # Seed database with sample data
make check-env      # Validate environment variables
```

## Key References

- [README.md](README.md) — Full tech stack, API reference, environment variables
- [GETTING_STARTED.md](GETTING_STARTED.md) — Setup walkthrough
- [CONTRIBUTING.md](CONTRIBUTING.md) — PR process and coding standards
- [SECURITY.md](SECURITY.md) — Security controls documentation
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Database and data flow decisions
- [docs/MONITORING.md](docs/MONITORING.md) — Prometheus/Grafana operations guide
