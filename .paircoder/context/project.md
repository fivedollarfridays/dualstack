# DualStack

## What Is This?

A production-ready SaaS starter kit combining FastAPI (Python) and Next.js (TypeScript). Extracted from a production AI chat platform, stripped to infrastructure skeleton with a generic "items" CRUD entity.

## Repository Structure

```
dualstack/
├── backend/         # FastAPI API (Python 3.13)
│   ├── app/
│   │   ├── core/    # Infrastructure (config, db, errors, logging, metrics)
│   │   ├── health/  # K8s health probes
│   │   ├── items/   # Generic CRUD entity
│   │   └── billing/ # Stripe integration
│   ├── tests/       # pytest (99% coverage)
│   └── alembic/     # DB migrations
├── frontend/        # Next.js 15 (TypeScript)
│   ├── src/
│   │   ├── app/     # Pages (dashboard, items, billing, settings, auth)
│   │   ├── components/ # UI components
│   │   ├── db/      # Drizzle + Turso
│   │   ├── lib/     # API clients, auth, utils
│   │   └── hooks/   # React Query hooks
│   └── drizzle/     # Frontend migrations
└── monitoring/      # Prometheus + Grafana + Alertmanager
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2, structlog |
| Frontend | Next.js 15, React 18, TypeScript 5, Tailwind CSS |
| Database | Turso/SQLite, Drizzle ORM, SQLAlchemy |
| Auth | Clerk |
| Payments | Stripe |
| Monitoring | Prometheus, Grafana |
| Testing | pytest, Jest, Playwright |

## Key Constraints

- Backend coverage: 99%
- Frontend coverage: 99%
- Max file length: 300 lines
- TDD workflow: tests first
