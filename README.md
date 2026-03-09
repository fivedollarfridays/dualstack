# DualStack

Production-ready **FastAPI + Next.js** SaaS starter kit with auth, payments, and monitoring out of the box.

## What's Included

- **FastAPI Backend** -- Python 3.13, async SQLAlchemy, Pydantic v2, structured logging, Prometheus metrics
- **Next.js 15 Frontend** -- App Router, TypeScript, Tailwind CSS, shadcn/ui components
- **Authentication** -- Clerk (backend JWT + frontend components)
- **Database** -- SQLite (Turso-ready) with Drizzle ORM (frontend) and SQLAlchemy (backend)
- **Payments** -- Stripe Checkout + Customer Portal
- **Monitoring** -- Prometheus + Grafana + Alertmanager (Docker Compose)
- **Health Checks** -- Kubernetes liveness + readiness probes
- **Background Jobs** -- APScheduler for async task scheduling
- **Testing** -- pytest (backend, 100% coverage) + Jest + Playwright (frontend, 100% coverage)
- **Generic CRUD Entity** -- "Items" module demonstrating the full pattern to extend

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Frontend | Next.js 15, React 18, TypeScript 5 |
| Database | SQLite (Turso-ready with configuration) |
| ORM | SQLAlchemy (backend), Drizzle (frontend) |
| Auth | Clerk |
| Payments | Stripe |
| Styling | Tailwind CSS, shadcn/ui |
| State | React Query, Zustand |
| Monitoring | Prometheus, Grafana, Alertmanager |
| Testing | pytest, Jest, Playwright |
| Deployment | Docker (backend), Vercel (frontend) |

## Project Structure

```
dualstack/
├── backend/                  # FastAPI API (Python 3.13)
│   ├── app/
│   │   ├── core/             # Infrastructure (config, db, errors, logging, metrics)
│   │   ├── health/           # K8s health probes
│   │   ├── items/            # Generic CRUD entity
│   │   └── billing/          # Stripe integration
│   ├── tests/                # pytest (100% coverage)
│   └── alembic/              # DB migrations
├── frontend/                 # Next.js 15 (TypeScript)
│   ├── src/
│   │   ├── app/              # Pages (dashboard, items, billing, settings, auth)
│   │   ├── components/       # UI components
│   │   ├── db/               # Drizzle + Turso
│   │   ├── lib/              # API clients, auth, utils
│   │   └── hooks/            # React Query hooks
│   └── drizzle/              # Frontend migrations
└── monitoring/               # Prometheus + Grafana + Alertmanager
    ├── docker-compose.yml
    ├── prometheus/
    ├── grafana/
    └── alertmanager/
```

## Quickstart

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
npm ci
cp .env.example .env.local

# Start services (separate terminals)
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
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

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /health/live | No | Liveness probe |
| GET | /health/ready | No | Readiness probe |
| GET | /metrics | No | Prometheus metrics |
| GET | /api/v1/items | Yes | List items |
| POST | /api/v1/items | Yes | Create item |
| GET | /api/v1/items/:id | Yes | Get item |
| PATCH | /api/v1/items/:id | Yes | Update item |
| DELETE | /api/v1/items/:id | Yes | Delete item |
| POST | /api/v1/billing/checkout | Yes | Create Stripe checkout |
| POST | /api/v1/billing/portal | Yes | Open billing portal |
| POST | /webhooks/stripe | No* | Stripe webhook |

*Verified by Stripe signature

## Running Tests

```bash
# Backend
cd backend
pip install -r requirements-dev.txt  # includes test dependencies
pytest --cov=app --cov-report=term-missing tests/

# Frontend
cd frontend
npm test
npm run test:coverage
```

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

## Customization

### Replacing "Items" with your domain entity

1. **Backend**: Copy `app/items/` to `app/your_entity/`, rename model, schemas, service, routes
2. **Frontend**: Copy `src/components/items/` and `src/app/(dashboard)/items/`, rename components and pages
3. **Database**: Update schemas in both backend (SQLAlchemy) and frontend (Drizzle)
4. **API client**: Update `src/lib/api/items.ts` to match new backend routes

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
3. Run `python scripts/stripe_sync.py` to sync plans to Stripe (edit `DEFAULT_PLANS` first)

## License

Personal Use License - Copyright (c) 2026 Kevin Masterson. See [LICENSE](LICENSE) for details.

