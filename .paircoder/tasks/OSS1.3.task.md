---
id: OSS1.3
title: Delete marketplace test files
plan: plan-sprint-1-engage
type: feature
priority: P0
complexity: 1
status: done
sprint: '1'
depends_on: []
completed_at: '2026-04-07T21:22:24.202291'
---

# Delete marketplace test files

Delete test files that validate the paid product experience: `tests/test_paircoder_branding.py`, `tests/test_listing_md.py`, `tests/test_buyer_experience.py`. Verify no other test files import from them. Update the README test count badge after deletion — recalculate with `pytest --co -q | tail -1` and update the badge number.

# Acceptance Criteria

- [x] `tests/test_paircoder_branding.py` deleted
- [x] `tests/test_listing_md.py` deleted
- [x] `tests/test_buyer_experience.py` deleted
- [x] `grep -rn "test_paircoder_branding\|test_listing_md\|test_buyer_experience" tests/` returns no results
- [x] README test count badge updated to actual count
- [x] Full test suite passes with no import errors