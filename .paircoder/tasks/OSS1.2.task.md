---
id: OSS1.2
title: Delete marketplace and internal artifacts
plan: plan-sprint-1-engage
type: feature
priority: P0
complexity: 1
status: done
sprint: '1'
depends_on: []
completed_at: '2026-04-07T21:19:12.576825'
---

# Delete marketplace and internal artifacts

Remove all files related to the paid marketplace listing and internal audit. Delete `badges/` directory (contains `LISTING.md`), delete `audit-report.md` from repo root, and verify `dualstack-sellable.md` is already gone (it's gitignored but may be tracked). Remove the sellable plan YAML from `.paircoder/plans/` if it exists in the tracked tree.

# Acceptance Criteria

- [x] `badges/` directory deleted
- [x] `audit-report.md` deleted
- [x] `dualstack-sellable.md` not tracked (`git ls-files dualstack-sellable.md` returns empty)
- [x] `git grep -l "sellable\|LISTING\.md"` returns no results in source files (excluding `.gitignore`)
- [x] All tests pass