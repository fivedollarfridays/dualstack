# Changelog

All notable changes to DualStack will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Process:** Add entries to `[Unreleased]` with each PR. At release time, move
unreleased entries into a new version section. Use conventional commit prefixes
(`feat:`, `fix:`, `security:`, `chore:`) and categorize entries accordingly.

## [Unreleased]

### Added
- Grafana alerting provisioning — error rate, auth failure, P99 latency alerts
- Incident response runbook (`docs/INCIDENT-RESPONSE.md`)
- Database backup script with RPO/RTO targets (`scripts/backup.sh`)
- Playwright E2E tests in CI pipeline
- Staging/production deployment workflow with approval gates
- Frontend Docker build verification in CI
- SOC2 compliance gap analysis updates (CC7.1, CC7.2, CC6.1)

## [1.0.0] - 2026-03-07

### Added
- FastAPI backend with SQLAlchemy 2.0 async ORM and Pydantic v2 schemas
- Next.js 15 frontend with App Router, TypeScript, and Tailwind CSS
- Clerk JWT authentication with JWKS validation and dev-mode bypass
- Items CRUD — full create, read, update, delete with user-scoped access
- Stripe billing integration — checkout sessions, billing portal, webhooks
- Users table with Clerk-to-Stripe mapping (Alembic migration)
- Feature gating via plan-based entitlements (free/pro/enterprise tiers)
- Dashboard with live subscription plan and status display
- Prometheus + Grafana + Alertmanager monitoring stack (Docker Compose)
- System Health, Database, and Background Jobs Grafana dashboards
- APScheduler background job framework with metrics
- React Query data fetching and Zustand state management
- Playwright E2E test suite (landing, dashboard, billing, items CRUD)
- Database seed script for development

### Security
- CORS configuration with explicit origin allowlist
- Rate limiting via SlowAPI on all endpoints
- Security headers (HSTS, nonce-based CSP, X-Frame-Options, X-Content-Type-Options)
- Audit logging on auth failures, webhook events, and CRUD operations
- Stripe webhook signature verification with empty-secret guard
- Bearer token authentication on /metrics endpoint (production)
- Streaming body size enforcement for chunked transfer encoding
- URL validation rejecting embedded credentials (userinfo component)
- DevAuthProvider production build guard (`process.env.NODE_ENV` check)
- Input validation via Pydantic schemas and Content-Length limits
- Prometheus UI basic-auth and Grafana-Prometheus auth

### Infrastructure
- Docker deployment for backend with multi-stage Dockerfile
- Render deployment configuration (`render.yaml`)
- GitHub Actions CI pipeline (backend tests, frontend tests, Docker build)
- Separate production and development configs
- SQLite/Turso database with Alembic migration system
- Structured logging via structlog
- Health probes (liveness + readiness) for container orchestration
