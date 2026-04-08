# Open Source Prep — DualStack

> Strip internal tooling references, marketplace artifacts, and sensitive data. Add standard community files and rewrite documentation for the open source audience. No new features — docs and cleanup only. Ships before the GitHub public push.

---

## Phase 1: Legal + Cleanup

### OSS1.1 — Replace LICENSE with MIT | Cx: 1 | P0

**Description:** Replace the current "Personal Use License" in `LICENSE` with the standard MIT license text. Copyright holder: Kevin Masterson. Year: 2026. Update any README references to the license type if they still say "Personal Use."

**AC:**
- [ ] `LICENSE` contains standard MIT license text
- [ ] Copyright line reads "Copyright (c) 2026 Kevin Masterson"
- [ ] `grep -i "personal use" LICENSE` returns no results
- [ ] README license badge/section references MIT, not Personal Use
- [ ] All tests pass, lint clean

**Depends on:** none

### OSS1.2 — Delete marketplace and internal artifacts | Cx: 1 | P0

**Description:** Remove all files related to the paid marketplace listing and internal audit. Delete `badges/` directory (contains `LISTING.md`), delete `audit-report.md` from repo root, and verify `dualstack-sellable.md` is already gone (it's gitignored but may be tracked). Remove the sellable plan YAML from `.paircoder/plans/` if it exists in the tracked tree.

**AC:**
- [ ] `badges/` directory deleted
- [ ] `audit-report.md` deleted
- [ ] `dualstack-sellable.md` not tracked (`git ls-files dualstack-sellable.md` returns empty)
- [ ] `git grep -l "sellable\|LISTING\.md"` returns no results in source files (excluding `.gitignore`)
- [ ] All tests pass

**Depends on:** none

### OSS1.3 — Delete marketplace test files | Cx: 1 | P0

**Description:** Delete test files that validate the paid product experience: `tests/test_paircoder_branding.py`, `tests/test_listing_md.py`, `tests/test_buyer_experience.py`. Verify no other test files import from them. Update the README test count badge after deletion — recalculate with `pytest --co -q | tail -1` and update the badge number.

**AC:**
- [ ] `tests/test_paircoder_branding.py` deleted
- [ ] `tests/test_listing_md.py` deleted
- [ ] `tests/test_buyer_experience.py` deleted
- [ ] `grep -rn "test_paircoder_branding\|test_listing_md\|test_buyer_experience" tests/` returns no results
- [ ] README test count badge updated to actual count
- [ ] Full test suite passes with no import errors

**Depends on:** none

### OSS1.4 — Add .paircoder and .claude to .gitignore | Cx: 1 | P0

**Description:** Add `.paircoder/` and `.claude/` to `.gitignore` so internal planning state and skill files are not included in the public repo. Then remove them from git tracking with `git rm -r --cached` so they stay on disk but are untracked. Verify they no longer appear in `git status` as tracked files.

**AC:**
- [ ] `.paircoder/` entry in `.gitignore`
- [ ] `.claude/` entry in `.gitignore`
- [ ] `git ls-files .paircoder/` returns empty
- [ ] `git ls-files .claude/` returns empty
- [ ] Files still exist on disk (not deleted, just untracked)
- [ ] All tests pass

**Depends on:** none

## Phase 2: Community Files

### OSS2.1 — Create CONTRIBUTING.md | Cx: 2 | P1

**Description:** Create a `CONTRIBUTING.md` with standard open source contribution guidelines tailored to DualStack. Include: prerequisites (Python 3.13, Node 20+, pnpm), setup instructions (`make setup`, env config), how to run tests (`make test`), PR process (fork, branch, test, submit), coding standards (ruff for Python, ESLint for TypeScript, architecture constraints), and where to ask questions (GitHub Issues). Reference the Makefile commands since they're the canonical dev interface.

**AC:**
- [ ] `CONTRIBUTING.md` exists at repo root
- [ ] Includes prerequisites section with version requirements
- [ ] Includes setup instructions referencing Makefile
- [ ] Includes test instructions for both backend and frontend
- [ ] Includes PR process (fork, branch, test, submit)
- [ ] Includes coding standards section
- [ ] File under 200 lines

**Depends on:** none

### OSS2.2 — Create CODE_OF_CONDUCT.md | Cx: 1 | P1

**Description:** Add the Contributor Covenant v2.1 as `CODE_OF_CONDUCT.md`. Set the enforcement contact to a project-appropriate email or GitHub Issues link. This is the standard adopted by most open source projects.

**AC:**
- [ ] `CODE_OF_CONDUCT.md` exists at repo root
- [ ] Uses Contributor Covenant v2.1 text
- [ ] Enforcement contact is set (not placeholder)
- [ ] File is complete and unmodified from the standard (except contact info)

**Depends on:** none

### OSS2.3 — Create GitHub issue and PR templates | Cx: 2 | P1

**Description:** Create `.github/ISSUE_TEMPLATE/bug_report.md` and `.github/ISSUE_TEMPLATE/feature_request.md` with structured templates. Create `.github/PULL_REQUEST_TEMPLATE.md` with a checklist covering: description, related issue, test coverage, and breaking changes. Keep templates concise — lower the barrier to contribution.

**AC:**
- [ ] `.github/ISSUE_TEMPLATE/bug_report.md` exists with structured fields (description, steps to reproduce, expected/actual behavior, environment)
- [ ] `.github/ISSUE_TEMPLATE/feature_request.md` exists with structured fields (problem, proposed solution, alternatives)
- [ ] `.github/PULL_REQUEST_TEMPLATE.md` exists with checklist (description, related issue, tests, breaking changes)
- [ ] Templates are concise (under 50 lines each)

**Depends on:** none

## Phase 3: Documentation Rewrite

### OSS3.1 — Rewrite CLAUDE.md as contributor guide | Cx: 2 | P1

**Description:** Replace the current `CLAUDE.md` (which contains bpsai-pair workflow instructions, Trello integration, containment mode, and internal CLI references) with a contributor-focused version. The new version should describe: project structure, how to add a new API endpoint (the "Items" pattern), how to add frontend pages, testing conventions (pytest for backend, Jest/Playwright for frontend), and architecture constraints (file size limits, function count limits). Strip all bpsai-pair, Trello, containment, and internal tooling references.

**AC:**
- [ ] `CLAUDE.md` contains no references to `bpsai-pair`, `ttask`, `trello`, `containment`, or internal tooling
- [ ] Describes project structure (backend/frontend/monitoring)
- [ ] Describes how to extend the codebase (add endpoint, add page)
- [ ] Describes testing conventions
- [ ] Describes architecture constraints
- [ ] `grep -i "bpsai\|trello\|containment\|ttask" CLAUDE.md` returns no results
- [ ] File under 150 lines

**Depends on:** none

### OSS3.2 — Polish README for open source audience | Cx: 3 | P1

**Description:** Update `README.md` to optimize for the open source audience (Python/FastAPI SaaS developers). Changes: (1) Update PairCoder link from `github.com/bpsai-labs/paircoder` to `paircoder.ai`. (2) Update test count badge to match actual count after test deletion. (3) Add a "Quick Start" section near the top (clone, make setup, make dev — 3 commands to running). (4) Add a "Why DualStack?" section highlighting differentiators: test count, security depth, monitoring stack, production-ready vs tutorial. (5) Ensure the "Built with PairCoder" section links to paircoder.ai. (6) Add "Contributing" section linking to CONTRIBUTING.md. (7) Add "License" section confirming MIT.

**AC:**
- [ ] PairCoder link points to `paircoder.ai`
- [ ] Test count badge matches actual count
- [ ] Quick Start section exists within first 50 lines
- [ ] "Why DualStack?" differentiator section exists
- [ ] Contributing section links to CONTRIBUTING.md
- [ ] License section confirms MIT
- [ ] `grep -i "bpsai-labs\|personal use\|sellable\|fivedollarfridays" README.md` returns no results
- [ ] No broken links (internal file references all resolve)

**Depends on:** OSS1.1, OSS1.3

### OSS3.3 — Update CHANGELOG and SECURITY contact | Cx: 1 | P1

**Description:** Add an entry to `CHANGELOG.md` for the open source transition (version bump to v2.0.0-oss or similar). Review `SECURITY.md` and ensure the security contact/disclosure process is appropriate for a public repo (email or GitHub Security Advisories, not an internal Slack channel). The current SECURITY.md content is excellent — likely just needs a contact info update.

**AC:**
- [ ] `CHANGELOG.md` has an entry for the open source release
- [ ] `SECURITY.md` has a public-appropriate disclosure contact
- [ ] No internal URLs or references in either file
- [ ] `grep -i "fivedollarfridays\|bpsai\|slack" SECURITY.md CHANGELOG.md` returns no results

**Depends on:** none

## Phase 4: Validation

### OSS4.1 — Final audit and test suite verification | Cx: 2 | P0

**Description:** Run a comprehensive audit to verify the repo is clean for public release. (1) Full test suite: `make test` — all tests pass. (2) CI check: verify GitHub Actions workflows don't reference internal services. (3) Secret scan: `grep -rn` for passwords, API keys, internal URLs, `fivedollarfridays`, `bpsai`, `devstack-store`, `sellable`, `personal use` across all tracked files. (4) Verify `.gitignore` covers `.paircoder/`, `.claude/`, `.env*`, `*.db`. (5) Verify no `.env` files are tracked. (6) Dry-run a `git archive` or `git ls-files` to see exactly what would be in the public repo.

**AC:**
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

**Depends on:** OSS1.1, OSS1.2, OSS1.3, OSS1.4, OSS2.1, OSS2.2, OSS2.3, OSS3.1, OSS3.2, OSS3.3

---

## Delivery Summary

| Phase | Tasks | Total Cx | Parallelism |
|-------|-------|----------|-------------|
| Phase 1: Legal + Cleanup | OSS1.1, OSS1.2, OSS1.3, OSS1.4 | 4 | All parallel |
| Phase 2: Community Files | OSS2.1, OSS2.2, OSS2.3 | 5 | All parallel |
| Phase 3: Documentation | OSS3.1, OSS3.2, OSS3.3 | 6 | OSS3.1 + OSS3.3 parallel, OSS3.2 after OSS1.1 + OSS1.3 |
| Phase 4: Validation | OSS4.1 | 2 | Sequential (depends on all) |
| **Total** | **11 tasks** | **17 Cx** | |

## Priority Order

1. OSS1.1 — MIT license (P0, blocks Phase 3)
2. OSS1.2 — Delete marketplace artifacts (P0)
3. OSS1.3 — Delete marketplace tests (P0, blocks Phase 3)
4. OSS1.4 — Gitignore internal dirs (P0)
5. OSS2.1 — CONTRIBUTING.md (P1)
6. OSS2.2 — CODE_OF_CONDUCT.md (P1)
7. OSS2.3 — Issue/PR templates (P1)
8. OSS3.1 — Rewrite CLAUDE.md (P1)
9. OSS3.2 — Polish README (P1)
10. OSS3.3 — Update CHANGELOG + SECURITY (P1)
11. OSS4.1 — Final audit (P0, gate)
