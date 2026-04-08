---
id: OSS1.3
title: Delete marketplace test files
plan: plan-sprint-1-engage
type: feature
priority: P0
complexity: 1
status: pending
sprint: '1'
depends_on: []
---

# Delete marketplace test files

Delete test files that validate the paid product experience: `tests/test_paircoder_branding.py`, `tests/test_listing_md.py`, `tests/test_buyer_experience.py`. Verify no other test files import from them. Update the README test count badge after deletion — recalculate with `pytest --co -q | tail -1` and update the badge number.

# Acceptance Criteria

- [ ] `tests/test_paircoder_branding.py` deleted
- [ ] `tests/test_listing_md.py` deleted
- [ ] `tests/test_buyer_experience.py` deleted
- [ ] `grep -rn "test_paircoder_branding\|test_listing_md\|test_buyer_experience" tests/` returns no results
- [ ] README test count badge updated to actual count
- [ ] Full test suite passes with no import errors
