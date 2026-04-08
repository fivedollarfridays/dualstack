---
id: OSS3.1
title: Rewrite CLAUDE.md as contributor guide
plan: plan-sprint-1-engage
type: feature
priority: P1
complexity: 2
status: pending
sprint: '1'
depends_on: []
---

# Rewrite CLAUDE.md as contributor guide

Replace the current `CLAUDE.md` (which contains bpsai-pair workflow instructions, Trello integration, containment mode, and internal CLI references) with a contributor-focused version. The new version should describe: project structure, how to add a new API endpoint (the "Items" pattern), how to add frontend pages, testing conventions (pytest for backend, Jest/Playwright for frontend), and architecture constraints (file size limits, function count limits). Strip all bpsai-pair, Trello, containment, and internal tooling references.

# Acceptance Criteria

- [ ] `CLAUDE.md` contains no references to `bpsai-pair`, `ttask`, `trello`, `containment`, or internal tooling
- [ ] Describes project structure (backend/frontend/monitoring)
- [ ] Describes how to extend the codebase (add endpoint, add page)
- [ ] Describes testing conventions
- [ ] Describes architecture constraints
- [ ] `grep -i "bpsai\|trello\|containment\|ttask" CLAUDE.md` returns no results
- [ ] File under 150 lines
