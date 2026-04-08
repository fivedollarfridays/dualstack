---
id: OSS3.3
title: Update CHANGELOG and SECURITY contact
plan: plan-sprint-1-engage
type: feature
priority: P1
complexity: 1
status: pending
sprint: '1'
depends_on: []
---

# Update CHANGELOG and SECURITY contact

Add an entry to `CHANGELOG.md` for the open source transition (version bump to v2.0.0-oss or similar). Review `SECURITY.md` and ensure the security contact/disclosure process is appropriate for a public repo (email or GitHub Security Advisories, not an internal Slack channel). The current SECURITY.md content is excellent — likely just needs a contact info update.

# Acceptance Criteria

- [ ] `CHANGELOG.md` has an entry for the open source release
- [ ] `SECURITY.md` has a public-appropriate disclosure contact
- [ ] No internal URLs or references in either file
- [ ] `grep -i "fivedollarfridays\|bpsai\|slack" SECURITY.md CHANGELOG.md` returns no results
