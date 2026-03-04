# DualStack

Production-ready **FastAPI + Next.js** SaaS starter kit with auth, payments, and monitoring out of the box.

## What's Included

- **FastAPI Backend** -- Python 3.13, async SQLAlchemy, Pydantic v2, structured logging, Prometheus metrics
- **Next.js 15 Frontend** -- App Router, TypeScript, Tailwind CSS, shadcn/ui components
- **Authentication** -- Clerk (backend JWT + frontend components)
- **Database** -- Turso/SQLite with Drizzle ORM (frontend) and SQLAlchemy (backend)
- **Payments** -- Stripe Checkout + Customer Portal
- **Monitoring** -- Prometheus + Grafana + Alertmanager (Docker Compose)
- **Health Checks** -- Kubernetes liveness + readiness probes
- **Background Jobs** -- APScheduler for async task scheduling
- **Testing** -- pytest (backend, 99% coverage) + Jest + Playwright (frontend, 99% coverage)
- **Generic CRUD Entity** -- "Items" module demonstrating the full pattern to extend

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Frontend | Next.js 15, React 18, TypeScript 5 |
| Database | Turso (LibSQL) / SQLite |
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
│   ├── tests/                # pytest (99% coverage)
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
- npm or pnpm

### 1. Clone and install

```bash
git clone <repo-url> dualstack
cd dualstack

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2. Configure environment

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your Turso, Clerk, Stripe keys

# Frontend
cp frontend/.env.example frontend/.env.local
# Edit frontend/.env.local with your Clerk, Stripe keys
```

### 3. Set up database

```bash
# Backend migrations
cd backend
alembic upgrade head

# Frontend migrations
cd ../frontend
npm run db:migrate
```

### 4. Start development

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Monitoring (optional)
cd monitoring
docker compose up -d
```

### 5. Open your browser

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

Or deploy to Render using the included `render.yaml`.

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

1. Create `app/your_module/routes.py` with FastAPI router
2. Import in `app/main.py` and include with prefix
3. Add service layer in `app/your_module/service.py`
4. Write tests first in `tests/your_module/`

## Built with PairCoder

This kit was extracted from a production application using [PairCoder](https://github.com/BPSAI/paircoder) -- AI-augmented pair programming.

## License

MIT

