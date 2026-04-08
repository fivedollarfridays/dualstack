---
id: OSS1.1
title: Replace LICENSE with MIT
plan: plan-sprint-1-engage
type: feature
priority: P0
complexity: 1
status: done
sprint: '1'
depends_on: []
completed_at: '2026-04-07T21:16:40.502019'
---

# Replace LICENSE with MIT

Replace the current "Personal Use License" in `LICENSE` with the standard MIT license text. Copyright holder: Kevin Masterson. Year: 2026. Update any README references to the license type if they still say "Personal Use."

# Acceptance Criteria

- [x] `LICENSE` contains standard MIT license text
- [x] Copyright line reads "Copyright (c) 2026 Kevin Masterson"
- [x] `grep -i "personal use" LICENSE` returns no results
- [x] README license badge/section references MIT, not Personal Use
- [x] All tests pass, lint clean