---
id: OSS2.1
title: Create CONTRIBUTING.md
plan: plan-sprint-1-engage
type: feature
priority: P1
complexity: 2
status: pending
sprint: '1'
depends_on: []
---

# Create CONTRIBUTING.md

Create a `CONTRIBUTING.md` with standard open source contribution guidelines tailored to DualStack. Include: prerequisites (Python 3.13, Node 20+, pnpm), setup instructions (`make setup`, env config), how to run tests (`make test`), PR process (fork, branch, test, submit), coding standards (ruff for Python, ESLint for TypeScript, architecture constraints), and where to ask questions (GitHub Issues). Reference the Makefile commands since they're the canonical dev interface.

# Acceptance Criteria

- [ ] `CONTRIBUTING.md` exists at repo root
- [ ] Includes prerequisites section with version requirements
- [ ] Includes setup instructions referencing Makefile
- [ ] Includes test instructions for both backend and frontend
- [ ] Includes PR process (fork, branch, test, submit)
- [ ] Includes coding standards section
- [ ] File under 200 lines
