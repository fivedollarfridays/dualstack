# DualStack — Product Page Copy
## For Gumroad + LemonSqueezy listings

---

### Product name
DualStack

### Tagline (one line, shows in search)
The Python-powered SaaS scaffold. FastAPI + Next.js 15 + Clerk + Stripe + Monitoring. Clone to running in 84 seconds.

### Price
$79 (one-time, lifetime updates)

---

### Description (paste into product description field)

Every SaaS boilerplate is JavaScript all the way down. DualStack isn't.

DualStack is a production-ready SaaS scaffold with a Python/FastAPI backend and a Next.js 15 frontend. You get async SQLAlchemy for the database, Pydantic v2 for validation, Clerk for auth, Stripe for payments, and a full Prometheus + Grafana + Alertmanager monitoring stack out of the box. No cobbling together tutorials. No "just add observability later." It's already there.

You get a complete, tested, audited codebase that goes from `git clone` to running in 84 seconds.

**What's in the box:**

- FastAPI backend with async SQLAlchemy, Pydantic v2, and structured logging (Python 3.13)
- Next.js 15 frontend with App Router, TypeScript, Tailwind CSS, and shadcn/ui
- SQLite (Turso-ready) or PostgreSQL — your choice of database
- Clerk authentication (JWT verification via JWKS, social login, MFA-ready)
- Stripe subscription billing with webhook handling and plan enforcement
- S3/R2-compatible file uploads with presigned URLs and content-type allowlisting
- Real-time WebSocket with JWT authentication and per-user message routing
- RBAC with admin, user, and custom roles
- Admin dashboard with user management, health checks, and audit logs
- Prometheus + Grafana + Alertmanager monitoring stack (Docker Compose)
- Background job scheduler (APScheduler)
- Makefile-driven setup — `make setup && make dev` and you're running
- Resend email integration for transactional email (infrastructure-ready)
- Environment configuration with `.env.example` for every service
- Generic CRUD entity ("Items") demonstrating the full-stack pattern to extend

**Why this exists:**

If you want to build a SaaS product with Python on the backend, your options today are: start from scratch and spend 3-4 weeks wiring up auth, payments, database, file uploads, monitoring, and WebSocket. Or use a JavaScript-only boilerplate and give up on Python entirely.

DualStack gives you the Python/FastAPI foundation with a modern Next.js frontend so you can start building your actual product on day one.

**The numbers:**

- 1,357 tests passing (95% coverage)
- 0 security vulnerabilities (audited, CVE patched)
- 863 backend tests + 494 frontend tests
- 102 kB shared JS bundle
- 84-second deploy time (clone to running)
- Built-in monitoring (Prometheus + Grafana + Alertmanager)
- All dependencies current

**12 things you won't find in other SaaS scaffolds:**

1. **Python + FastAPI backend** — Async, battle-tested, type-safe with Pydantic v2. Not another all-JavaScript stack
2. **Database flexibility** — Turso/SQLite for simplicity or PostgreSQL for scale. Switch with a config change
3. **Built-in monitoring stack** — Prometheus + Grafana + Alertmanager with pre-configured dashboards and alert rules
4. **WebSocket with per-user isolation** — JWT-authenticated real-time events scoped to the owning user. No broadcast leaks
5. **Makefile-driven setup** — `make setup && make dev`. One command to install deps, create env files, run migrations, and start everything
6. **Background job scheduler** — APScheduler for async tasks, cron jobs, and recurring work. Not bolted on later
7. **PII scrubbing** — Webhook payloads have email/name/phone stripped before logging. GDPR-conscious from day one
8. **File upload security** — Content-type allowlisting blocks SVG/HTML/JS uploads. Filenames sanitized against path traversal
9. **Admin dashboard** — User management, role assignment, health checks, audit log viewer
10. **Comprehensive SECURITY.md** — 6.7 KB of documented security controls with source file references
11. **Rename script** — `python scripts/rename.py --from item --to project` renames the reference entity across the entire codebase
12. **Structured logging** — JSON output with structlog, request IDs, and log levels. Production-ready from the start

**Who this is for:**

Developers and indie hackers who want Python on the backend and React on the frontend. You should be comfortable with FastAPI, Next.js, and SQL. This is a codebase, not a no-code tool.

**What you get after purchase:**

GitHub repo access with full source code. Lifetime updates. No subscription, no recurring fees. Built with [PairCoder](https://github.com/bpsai-labs/paircoder) -- AI-augmented pair programming with enforcement gates and sprint-based delivery.

---

### Competitive comparison (use as a table or image on listing page)

| Feature | DualStack ($79) | ShipFast ($179) | Supastarter ($299) | Makerkit ($249) |
|---------|:-:|:-:|:-:|:-:|
| Test coverage | 95% (1,357 tests) | Minimal | Partial | Partial |
| Backend language | Python (FastAPI) | Node.js | Node.js | Node.js |
| Database options | SQLite + PostgreSQL | PostgreSQL | PostgreSQL/Supabase | PostgreSQL/Supabase |
| Monitoring stack | Prometheus + Grafana + Alertmanager | No | No | No |
| WebSocket (real-time) | JWT-authenticated, per-user | No | No | Basic |
| Background jobs | APScheduler | No | No | No |
| File uploads | S3/R2 presigned URLs | Basic | Basic | Basic |
| Admin dashboard | Built-in | No | Basic | Basic |
| Security documentation | SECURITY.md (6.7 KB) | Basic | Basic | Basic |
| Clone-to-running | 84 seconds | ~5 min | ~10 min | ~5 min |
| RBAC | Built-in | No | Add-on | Add-on |
| CI/CD | Full pipeline + auto-merge | Basic | Basic | Basic |

---

### What's NOT included (and why)

| Feature | Reason |
|---------|--------|
| Multi-tenancy | DualStack is single-tenant by design. Multi-tenancy adds significant complexity that most early-stage SaaS products don't need. Build it when you need it |
| Dunning / payment recovery | Stripe handles retry logic natively. Adding custom dunning on top is only needed at scale |
| E2E test suite | Playwright is configured but E2E tests require a deployed instance with real Clerk/Stripe keys. Unit + integration tests cover all code paths |
| Marketing pages / blog | Use your preferred CMS or static site generator. DualStack focuses on the authenticated app, not the landing page |
| Global rate limiting | SlowAPI handles per-endpoint rate limiting. Infrastructure-level rate limiting (Cloudflare, AWS WAF) is a deployment concern, not a codebase concern |

---

### Badge row (paste into README and product images)

```
![Tests](https://img.shields.io/badge/tests-1%2C357_passing-brightgreen) ![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen) ![Security](https://img.shields.io/badge/vulnerabilities-0-brightgreen) ![Bundle](https://img.shields.io/badge/bundle-102_kB-blue) ![Deploy](https://img.shields.io/badge/deploy-84_seconds-blue) ![Deps](https://img.shields.io/badge/deps-up_to_date-brightgreen) ![Built with PairCoder](https://img.shields.io/badge/built%20with-PairCoder-blueviolet)
```

---

### Thumbnail / hero image text (for the product card image)

**Line 1 (large):** DualStack
**Line 2 (medium):** Python-powered SaaS scaffold
**Line 3 (small, badge row):** 1,357 tests | 0 vulnerabilities | 84s deploy
**Line 4 (price):** $79 one-time

---

### FAQ (add to product page if the platform supports it)

**Is this a template or a full codebase?**
Full codebase. You get the complete source code with all dependencies, tests, and configuration. Fork it, modify it, ship it.

**What version of Python does this use?**
Python 3.13. The backend uses FastAPI with async SQLAlchemy 2.0 and Pydantic v2. All modern Python async patterns.

**Can I use PostgreSQL instead of SQLite?**
Yes. DualStack supports both Turso/SQLite (great for development and small deployments) and PostgreSQL (for production scale). Switch by changing the `DATABASE_URL` environment variable. Alembic migrations work with both.

**What about updates?**
Lifetime updates via the GitHub repo. When dependencies get major bumps or security patches land, the scaffold gets updated.

**Can I use this for multiple projects?**
Yes. One purchase, unlimited projects. Build as many products as you want on it.

**How do I replace the "Items" entity with my own?**
Run `python scripts/rename.py --from item --to your_entity`. It renames files, directories, classes, variables, routes, and imports across the entire codebase. Supports irregular plurals with `--to-plural`.

**What's your refund policy?**
If the code doesn't match the description — tests don't pass, features are missing, or the scaffold doesn't build — you get a full refund. Run `make test` within 24 hours of purchase and let us know if anything's off.

---

### SEO keywords (for Gumroad tags)
python saas boilerplate, fastapi saas starter, fastapi next.js template, saas scaffold python, python saas starter kit, fastapi boilerplate 2026, next.js fastapi, indie hacker python, saas template fastapi, python backend react frontend

---

### Account setup notes

You need to create accounts on both platforms yourself:
- Gumroad: https://gumroad.com (sign up > create product > digital product > paste copy above)
- LemonSqueezy: https://lemonsqueezy.com (sign up > create store > new product > paste copy above)

Both platforms handle payment processing, delivery (GitHub repo access), and tax compliance. Gumroad takes 10%, LemonSqueezy takes 5% + payment processing. LemonSqueezy is the better margin long-term.
