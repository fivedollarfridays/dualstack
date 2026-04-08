---
id: OSS4.1
title: Final audit and test suite verification
plan: plan-sprint-1-engage
type: feature
priority: P0
complexity: 2
status: pending
sprint: '1'
depends_on:
- OSS1.1
- OSS1.2
- OSS1.3
- OSS1.4
- OSS2.1
- OSS2.2
- OSS2.3
- OSS3.1
- OSS3.2
- OSS3.3
---

# Final audit and test suite verification

Run a comprehensive audit to verify the repo is clean for public release. (1) Full test suite: `make test` — all tests pass. (2) CI check: verify GitHub Actions workflows don't reference internal services. (3) Secret scan: `grep -rn` for passwords, API keys, internal URLs, `fivedollarfridays`, `bpsai`, `devstack-store`, `sellable`, `personal use` across all tracked files. (4) Verify `.gitignore` covers `.paircoder/`, `.claude/`, `.env*`, `*.db`. (5) Verify no `.env` files are tracked. (6) Dry-run a `git archive` or `git ls-files` to see exactly what would be in the public repo.

# Acceptance Criteria

- [ ] `make test` passes (both backend and frontend)
- [ ] `git grep -i "fivedollarfridays"` returns no results
- [ ] `git grep -i "devstack-store"` returns no results
- [ ] `git grep -i "sellable"` returns no results (excluding .gitignore)
- [ ] `git grep -i "personal use license"` returns no results
- [ ] `git grep -l "\.env"` returns only `.env.example` files and `.gitignore`
- [ ] No tracked `.env`, `.env.local`, or `.env.production` files
- [ ] GitHub Actions workflows contain no internal service references
- [ ] `git ls-files .paircoder/ .claude/` returns empty
- [ ] CI passes locally
