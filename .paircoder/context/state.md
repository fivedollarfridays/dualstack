# Current State

Project: DualStack
Status: v1.0.0 — Sprint 18 complete, production readiness fixes applied

## Active Plans

### Completed
- **plan-2026-03-launch-prep** — Complete
- **plan-2026-03-release-hardening** — Complete (T5.1-T5.8)
- **plan-2026-03-market-readiness** — Complete (T6.1-T6.6)
- **plan-2026-03-security-remediation** — Complete (T7.1-T7.6)
- **plan-2026-03-security-hardening-r2** — Complete (T8.1-T8.6)
- **plan-2026-03-security-hardening-r3** — Complete (T9.1-T9.7)
- **plan-2026-03-security-hardening-r4** — Complete (T10.1-T10.4)
- **plan-2026-03-billing-subscriptions** — Complete (T13.1-T13.5)
- **plan-2026-03-production-readiness-fixes** — Complete (T18.1-T18.7, 185 complexity)

### Planned (Pending)
- **plan-2026-03-security-hardening-r5** — S11: Security R5 Remediation (T11.1-T11.4, 105 complexity)
  - T11.1 (P1, 45): Streaming body size enforcement for chunked transfer encoding
  - T11.2 (P1, 25): Backend URL validation — reject embedded credentials
  - T11.3 (P2, 20): DevAuthProvider production build guard
  - T11.4 (P2, 15): Config cleanup — Stripe key prefix + Prometheus dev auth docs
- **plan-2026-03-database-architecture** — S12: Database Architecture (T12.1-T12.4, 170 complexity)
  - T12.1 (P1, 80): Evaluate sqlalchemy-libsql or PostgreSQL migration
  - T12.2 (P1, 25): Remove or justify frontend DB layer
  - T12.3 (P2, 35): Consolidate to single migration system [depends: T12.2]
  - T12.4 (P2, 30): Create database seed script
- **plan-2026-03-soc2-cicd** — S14: SOC2 P1 + CI/CD (T14.1-T14.7, 235 complexity)
  - T14.1 (P1, 40): Grafana alert rules
  - T14.2 (P1, 30): Incident response runbook
  - T14.3 (P1, 50): Automated database backups + RPO/RTO
  - T14.4 (P1, 35): Playwright E2E in CI
  - T14.5 (P1, 45): Staging/production deployment stages
  - T14.6 (P2, 20): Frontend Docker build in CI
  - T14.7 (P2, 15): CHANGELOG.md
- **plan-2026-03-dx-soc2-p2** — S15: DX + SOC2 P2 (T15.1-T15.7, 225 complexity)
  - T15.1 (P1, 30): Makefile for single-command dev setup
  - T15.2 (P2, 20): Central configuration reference
  - T15.3 (P1, 50): Log aggregation with Fluent Bit
  - T15.4 (P2, 35): Uptime monitoring + PagerDuty
  - T15.5 (P2, 25): On-call rotation + PIR process
  - T15.6 (P2, 35): Tested restore process + backup monitoring [depends: T14.3]
  - T15.7 (P3, 30): Monorepo workspace config
- **plan-2026-03-saas-features-p1** — S16: SaaS Features Phase 1 (T16.1-T16.5, 270 complexity)
  - T16.1 (P1, 65): Email/notification system
  - T16.2 (P1, 70): RBAC — roles and permissions
  - T16.3 (P1, 60): Admin dashboard [depends: T16.2]
  - T16.4 (P2, 40): User profile management
  - T16.5 (P2, 35): Search, sort, filter on list endpoints
- **plan-2026-03-saas-features-p2** — S17: SaaS Features Phase 2 (T17.1-T17.6, 225 complexity)
  - T17.1 (P2, 50): File upload with S3/R2
  - T17.2 (P2, 55): Real-time WebSocket/SSE
  - T17.3 (P2, 35): Onboarding flow
  - T17.4 (P3, 40): Marketing pages + blog
  - T17.5 (P3, 20): SEO (sitemap, robots.txt)
  - T17.6 (P3, 25): Analytics integration

### Active
- **plan-2026-03-dualstack-get-sellable** — S23: Get DualStack Sellable (T23.1-T23.5, 60 complexity)
  - T23.1 (P1, 25): Write LISTING.md ✓
  - T23.2 (P2, 5): Add PairCoder branding ✓
  - T23.3 (P1, 15): Create devstack-store product definition [depends: T23.1] ✓
  - T23.4 (P2, 5): Verify Stripe price IDs ✓
  - T23.5 (P1, 10): Smoke test buyer experience ✓

## Current Focus

Sprint 23 (Get DualStack Sellable) — T23.1, T23.2, T23.3, T23.4, T23.5 all complete. Sprint done.

## What Was Just Done

- **T23.3 done** -- Created devstack-store product definition for DualStack. Created `packages/shared/src/products/dualstack.ts` mirroring edgestack.ts structure with: slug 'dualstack', category 'fullstack', 10-item techStack (FastAPI, Next.js 15, SQLAlchemy, etc.), 3 tiers (Starter free, Pro $79, Enterprise $199) with placeholder Stripe price IDs, 12 features pulled from LISTING.md differentiators. Updated `products/index.ts` to export DUALSTACK and include it in PRODUCTS array. Added 14 tests to product.test.ts covering schema validation, tier pricing, tech stack contents, and slug lookup. All 259 shared package tests passing, TypeScript compiles clean across all 8 packages.

- **T23.2 done** -- Added PairCoder branding. README.md already had the badge in the badge row and a descriptive mention. LISTING.md already had the badge in the badge code block. Added "Built with PairCoder" mention to the "What you get after purchase" section of LISTING.md (outside the code block). 7 validation tests in tests/test_paircoder_branding.py. All acceptance criteria pass: grep -i paircoder returns results for both files.

- **T23.5 done** -- Buyer experience smoke test. Audited GETTING_STARTED.md, README.md, Makefile, env examples, and all critical paths. Found and fixed 7 friction points: (1) Makefile setup used `npm ci` instead of `pnpm install`, (2) Makefile dev used `npm run dev` instead of `pnpm dev`, (3) Makefile test used `npm test` instead of `pnpm test`, (4) Makefile lint used `npm run lint` instead of `pnpm lint`, (5) No `.python-version` file for pyenv users, (6) No `.nvmrc` file for nvm users, (7) GETTING_STARTED.md seed command was `python scripts/seed.py` (wrong) instead of `make seed` / `python -m scripts.seed`. All fixed. 26 regression tests in tests/test_buyer_experience.py.

- **T23.1 done** (auto-updated by hook)

- **T23.1 done** -- Created badges/LISTING.md marketplace listing document matching EdgeStack structure. Includes: product name, tagline, $79 pricing, 3-paragraph description emphasizing Python/FastAPI positioning, "What's in the box" (15 features), "Why this exists" positioning, 12-point differentiator list, competitive comparison table vs ShipFast/Supastarter/Makerkit, "What's NOT included" table, badge row (1,334 tests, 95% coverage, 0 vulnerabilities), thumbnail spec, 7-question FAQ, SEO keywords, account setup notes. 17 validation tests in tests/test_listing_md.py.

- **T23.4 done** -- Verified all Stripe price ID references across the codebase. No hardcoded real Stripe IDs found. All source code uses env var references (`NEXT_PUBLIC_STRIPE_PRO_PRICE_ID`) with a descriptive fallback (`price_pro_monthly`). frontend/.env.example has correct placeholder (`price_your_pro_plan_id`). Backend validates price_id format via regex (`^price_[a-zA-Z0-9]+$`). Test files use synthetic IDs (`price_abc`, `price_pro`). Documentation correctly references the env var. No bugs, no changes needed.

- **Sprint 23 planned** — Created plan-2026-03-dualstack-get-sellable (chore, 60 complexity, 5 tasks). Tasks: T23.1 Write LISTING.md (25), T23.2 Add PairCoder branding (5), T23.3 Create devstack-store product definition (15), T23.4 Verify Stripe price IDs (5), T23.5 Smoke test buyer experience (10). All 5 cards synced to Trello Planned/Ready list.


- **Plan created: plan-2026-03-tenantforge-extraction** -- Created plan YAML and 8 task files (T1-T8) for Qluo/TenantForge extraction across 4 sprints (300 pts total). Sprint 1: repo setup + 11 module transfer. Sprint 2: dual-purpose module triage + reference entity. Sprint 3: frontend adaptation + documentation. Sprint 4: test suite + DevStack Store listing.

- **T22.3 done** -- Webhook PII scrubbing + smoke test script. Created `backend/app/billing/pii.py` with `scrub_pii()` function that strips customer email, name, address, phone from webhook event data (including nested billing_details, shipping, and charges objects) while preserving business IDs (customer, subscription, charge IDs). Integrated into `handle_webhook` in service.py so debug and error logs use scrubbed data instead of raw PII. 11 tests in `test_pii_scrubbing.py` (9 unit + 2 integration). Created `scripts/smoke_test.sh` (executable) checking health endpoints, auth enforcement (401), method enforcement (405), and 404 handling with `--help` and `--url` options. Added `make smoke` target to Makefile. 74 billing tests passing, no regressions.

- **Toast notifications added** -- Installed sonner (pinned 2.0.7), added `<Toaster />` to providers.tsx (both Clerk and dev branches), added success/error toasts to all item mutation hooks (useCreateItem, useUpdateItem, useDeleteItem) in use-items.ts, added success/error toasts to profile save and error toast to account deletion in profile page.tsx. 9 new toast tests in use-items.test.ts, 2 new Toaster rendering tests in providers.test.tsx, 3 new profile page toast tests in page.test.tsx. 493 frontend tests passing, zero regressions.

- **T22.4 done** -- Pre-commit hooks: created .pre-commit-config.yaml with pre-commit-hooks (trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files --maxkb=500) and ruff-pre-commit (ruff --fix, ruff-format). Added lint and format Makefile targets. Added ruff to requirements-dev.txt. Fixed 6 ruff lint errors (5 F841 unused variables in test files, 1 E402 import order in email_templates/__init__.py). Fixed formatting across 77 files via ruff-format. All pre-commit hooks pass clean. 17 validation tests in tests/test_precommit_config.py. 863 backend tests passing.

- **T22.5 done** -- Dependabot auto-merge workflow: created .github/workflows/dependabot-auto-merge.yml that auto-merges patch-level Dependabot PRs via gh pr merge --auto --squash. Updated README badge from 1327 to 1334 tests (852 backend + 482 frontend).

- **T21.3 done** -- Enhanced seed script: changed SEED_USER_ID to "dev-user-001", added `seed_user()` function to create demo user (clerk_user_id="dev-user-001", role="member"), reduced SAMPLE_ITEMS from 7 to 5 with correct status distribution (2 active, 2 draft, 1 archived), added `days_ago` field for spaced `created_at` timestamps over last 7 days, added `make seed` target to Makefile. 9 tests in test_seed.py covering user creation, idempotency, item count, status distribution, timestamps, and realistic titles. 850 backend tests passing.

- **T21.5 done** -- Verified OpenAPI docs configuration (docs_url/redoc_url/openapi_url correctly disabled in production, enabled in dev). Verified deployment artifacts: docker-compose.yml (backend + frontend services with healthchecks), render.yaml (backend web service config), backend/Dockerfile (Python 3.13-slim, non-root user), frontend/Dockerfile (multi-stage Node.js build). All complete and correct, no changes needed.

- **T21.1 done** -- Rewrote README.md (483 lines) and created GETTING_STARTED.md (339 lines). README now includes: updated badges (1327 tests, 95% coverage), full 24-endpoint API table organized by module, complete environment variables reference (backend + frontend), Stripe webhook setup with test cards, plan tiers table (free/pro/enterprise), security notes (CSP, rate limiting, input validation, JWT auth, audit logging), operations section (health checks, Prometheus metrics, monitoring stack, backups), updated project structure with all modules. GETTING_STARTED.md covers prerequisites, install (Makefile + manual), env config (minimum + full), database setup, seed data, dev server, verification URLs, next steps (items, billing, uploads, customization), and troubleshooting.

- **T21.4 done** — Created SECURITY.md (93 lines) documenting all security controls verified against source code. Covers CSP, authentication, authorization, input validation, rate limiting, webhook security, file upload security, environment validation, audit logging, cookie security, and WebSocket security. Added tests/test_security_md.py with 5 tests validating existence, length, required sections, no marketing language, and source file references.

- **T21.2 done** — Created `scripts/check_env.py` (stdlib-only) to validate backend/.env and frontend/.env.local: checks required vars (DATABASE_URL/TURSO_DATABASE_URL, CLERK_JWKS_URL, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, METRICS_API_KEY, NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, NEXT_PUBLIC_API_URL), warns on optional vars (RESEND_API_KEY, STORAGE_*, CORS_ORIGINS), rejects placeholders (changeme, your-key-here, etc.), colorized output. Added `check-env` Makefile target and integrated into `setup` (non-blocking). Updated backend/.env.example with all Settings model vars (added CLERK_AUDIENCE, LOG_FORMAT, STORAGE_*, FORWARDED_ALLOW_IPS). 24 tests in scripts/test_check_env.py, all passing.

- **T19.5 done** (auto-updated by hook)

- **T19.4 done** (auto-updated by hook)

- **T19.3 done** (auto-updated by hook)

- **T19.2 done** (auto-updated by hook)

- **T19.1 done** (auto-updated by hook)

- **T19.4 done** — Rate limit health endpoints + proxy hardening. Added `@limiter.limit("120/minute")` and `request: Request` param to `readiness` and `health` endpoints in checks.py (liveness left unlimited -- no I/O). Added `forwarded_allow_ips: str = "127.0.0.1"` to Settings in config.py. Added production startup warning in main.py lifespan when FORWARDED_ALLOW_IPS is default. 3 new rate limit tests in test_checks.py, 2 config tests + 3 warning tests in test_proxy_hardening.py. 48 tests passing across affected files, no regressions.

- **T19.1 done** — File upload content_type allowlist + storage_key leak removal. Added `ALLOWED_CONTENT_TYPES` frozenset and `field_validator("content_type")` on `UploadUrlRequest` in schemas.py (blocks text/html, image/svg+xml, application/octet-stream, application/javascript, text/xml). Removed `storage_key` field from `UploadUrlResponse` schema. Updated `request_upload_url` in service.py to not return storage_key in result dict (still used internally for S3). 16 new schema validation tests, 3 new route-level content_type tests. Updated existing tests that asserted storage_key in responses or used disallowed content types. 832 backend tests passing, no regressions.

- **T19.2 complete** — Fixed ValueError producing 500 instead of 404 in users/service.py: replaced both `raise ValueError(...)` with `raise NotFoundError(message="User not found")` in `update_user` and `link_stripe_customer`. Added missing audit events to file read routes: `persist_audit_event` with action="list" on `list_files_route` and action="download_request" on `get_download_url_route`. Updated 2 existing tests from ValueError to NotFoundError assertions, added 2 new audit event tests. 26 tests passing across both files, no regressions.

- **T19.5 done** — Input sanitization + npm pinning + CSP expansion. Added `field_validator` on `display_name` in `UserProfileUpdate` to strip `<` and `>` characters (prevents stored XSS). Pinned all npm dependencies to exact versions (removed `^` prefix from all 29 deps in package.json). Expanded CSP header from `default-src 'self'` to include `script-src 'none'; style-src 'none'; frame-ancestors 'none'; form-action 'none'`. 5 new display_name sanitization tests, 1 new CSP directive test. 830 backend tests passing, no regressions.

- **T19.3 done** — WebSocket JWT audience validation + broadcast() removal. Added `clerk_audience` setting to config.py. Updated `_verify_token` in ws_auth.py to validate JWT `aud` claim when `clerk_audience` is configured (rejects wrong audience), and skip audience validation when empty (dev backward compat). Removed `broadcast()` method from ConnectionManager in websocket.py (security footgun). 3 new audience validation tests, 1 new no-broadcast assertion test. 23/23 affected tests passing, no regressions.

- **T18.7 done** (auto-updated by hook)

- **T18.4 done** (auto-updated by hook)

- **T18.3 done** (auto-updated by hook)

- **T18.2 done** (auto-updated by hook)

- **T18.1 done** (auto-updated by hook)

- **T18.7 complete** — Dependency pinning + npm audit fix + CSP nonce + dev token guard. Pinned 3 open-ended pip deps to exact versions (prometheus-client==0.21.0, resend==2.23.0, APScheduler==3.11.2). Fixed HIGH-severity npm vulnerability in `flatted` via `npm audit fix`. Replaced `'unsafe-inline'` with `'nonce-${nonce}'` in CSP style-src directive. Added `getDevToken()` with localhost guard and `isLocalDev()` helper to prevent dev token leaking on production hostnames. Updated dev-auth-provider to use `getDevToken()`. 451 frontend tests passing, 808 backend tests passing, no regressions.
- **T18.6 complete** — Security hardening: added `field_validator` on `avatar_url` in `UserProfileUpdate` rejecting non-HTTPS schemes (blocks `javascript:`, `data:`, `http://`, `ftp:` XSS vectors). Added `PurePosixPath.name` filename sanitization in `files/service.py` to strip path traversal (`../../etc/passwd` -> `passwd`). 8 new avatar URL validation tests, 4 new filename sanitization tests. `get_client_ip` docstring already present. 800 backend tests passing, no regressions.
- **T18.3 complete** — Fixed WebSocket broadcast leak (OWASP A01:2021 broken access control). Changed `_broadcast_event` in ws_routes.py from `manager.broadcast()` to `manager.send_to_user(user_id, payload)`, so item events are only sent to the owning user. Events missing `user_id` are now dropped with a warning log. Added 3 user-isolation tests in test_websocket_manager.py. All 529 core tests passing, no regressions.
- **T18.5 complete** — Replaced all 3 raw HTTPException raises with custom AppError subclasses (NotFoundError, AuthorizationError) in billing/routes.py, core/entitlements.py, core/metrics_routes.py. All error responses now use standard {"error": {"code", "message"}} envelope. Added return type annotations to all billing route handlers. Switched billing audit from log_audit_event to persist_audit_event (DB-persisted). Fixed FileResponse Pydantic v1 class Config to v2 model_config. Zero HTTPException usage remaining in backend/app/. 785 tests passing, no regressions.
- **T18.4 complete** — Fixed frontend build lint error (`@typescript-eslint/no-explicit-any` in use-websocket.test.ts) and cleaned up all lint warnings in test files: removed unused `children` param in sign-in/sign-up mocks, removed unused `React` import in use-realtime-items.test.ts, switched `Object.entries` to `Object.values` in clerk-config.test.ts. Build compiles successfully, all 39 affected tests pass.
- **T18.2 complete** — Registered files router at `/api/v1/files` and WebSocket router at `/ws` in `_register_routers()` in main.py. Added 5 storage config fields (storage_bucket, storage_access_key, storage_secret_key, storage_endpoint, storage_region) to Settings in config.py. Added production startup warning when storage is not configured. 5 new tests in test_main.py (router registration + storage config + storage warning). All 9 file route tests now pass. 29/29 test_main.py tests green. No regressions (777 passing).
- **T18.1 complete** — Fixed CRITICAL WebSocket JWT verification vulnerability.

## What's Next

T23.1 complete. Next: T23.2 (Add PairCoder branding) or T23.3 (Create devstack-store product definition, depends on T23.1 which is now done).
