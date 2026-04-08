---
id: OSS1.4
title: Add .paircoder and .claude to .gitignore
plan: plan-sprint-1-engage
type: feature
priority: P0
complexity: 1
status: pending
sprint: '1'
depends_on: []
---

# Add .paircoder and .claude to .gitignore

Add `.paircoder/` and `.claude/` to `.gitignore` so internal planning state and skill files are not included in the public repo. Then remove them from git tracking with `git rm -r --cached` so they stay on disk but are untracked. Verify they no longer appear in `git status` as tracked files.

# Acceptance Criteria

- [ ] `.paircoder/` entry in `.gitignore`
- [ ] `.claude/` entry in `.gitignore`
- [ ] `git ls-files .paircoder/` returns empty
- [ ] `git ls-files .claude/` returns empty
- [ ] Files still exist on disk (not deleted, just untracked)
- [ ] All tests pass
