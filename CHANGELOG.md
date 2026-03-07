# Changelog

All notable changes to DualStack will be documented in this file.

## [1.0.0] - 2026-03-07

### Initial Release

**Backend (FastAPI)**
- REST API with FastAPI, SQLAlchemy 2.0, Pydantic v2
- Clerk JWT authentication with dev-mode bypass
- Stripe Checkout integration and webhook handler
- SQLite database with Alembic migrations
- Prometheus metrics endpoint
- Kubernetes health probes (liveness + readiness)
- APScheduler background jobs
- Security headers, rate limiting, structured logging
- 100% test coverage (pytest)

**Frontend (Next.js 15)**
- App Router with TypeScript and Tailwind CSS
- Clerk authentication (sign-in, sign-up, user button)
- Dashboard, Items CRUD, Billing, and Settings pages
- Drizzle ORM with SQLite/Turso support
- React Query data fetching + Zustand state management
- shadcn/ui component library
- Security headers via next.config.mjs
- 100% test coverage (Jest + Playwright)

**Monitoring**
- Prometheus + Grafana + Alertmanager (Docker Compose)
- System Health, Database, and Background Jobs dashboards
- Critical, warning, and info alert rules

**Infrastructure**
- Docker deployment for backend
- Vercel deployment for frontend
- Separate production and development configs
- `.dockerignore` for lean production images
- Split `requirements.txt` / `requirements-dev.txt`
