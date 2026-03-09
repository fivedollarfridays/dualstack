# Post-Incident Review (PIR) Template

Use this template after resolving a production incident. Copy this file,
fill in the sections, and store the completed PIR in `docs/pirs/`.

---

## Metadata

| Field | Value |
|-------|-------|
| **Incident ID** | INC-YYYY-NNN |
| **Date** | YYYY-MM-DD |
| **Severity** | SEV1 / SEV2 / SEV3 |
| **Duration** | HH:MM (detection to resolution) |
| **Author** | Name |
| **Attendees** | Name1, Name2, ... |

---

## Timeline

Chronological list of events from detection to resolution.

| Time (UTC) | Event |
|------------|-------|
| HH:MM | Alert fired / issue reported |
| HH:MM | On-call acknowledged |
| HH:MM | Triage began — initial assessment |
| HH:MM | Root cause identified |
| HH:MM | Fix deployed |
| HH:MM | Monitoring confirmed resolution |

---

## Impact

- **Users affected:** Number or percentage of users impacted
- **Services impacted:** List of affected services/endpoints
- **Data loss:** Yes/No — describe if applicable
- **SLA breach:** Yes/No — which SLA was breached
- **Revenue impact:** Estimated if applicable

---

## Root Cause Analysis

Use the **5 Whys** method to identify the root cause:

1. **Why** did the incident occur?
   → _Answer_
2. **Why** did that happen?
   → _Answer_
3. **Why** did that happen?
   → _Answer_
4. **Why** did that happen?
   → _Answer_
5. **Why** did that happen?
   → _Root cause_

**Root cause summary:** _One sentence describing the fundamental cause._

---

## Contributing Factors

Non-root-cause items that made the incident worse or delayed resolution:

- _Factor 1_
- _Factor 2_
- _Factor 3_

---

## What Went Well

Things that worked during incident response:

- _Item 1_
- _Item 2_
- _Item 3_

---

## Action Items

| # | Description | Owner | Due Date | Status |
|---|-------------|-------|----------|--------|
| 1 | _Action_ | _Name_ | YYYY-MM-DD | Open |
| 2 | _Action_ | _Name_ | YYYY-MM-DD | Open |
| 3 | _Action_ | _Name_ | YYYY-MM-DD | Open |

---

## Lessons Learned

Key takeaways for the team:

1. _Lesson 1_
2. _Lesson 2_
3. _Lesson 3_

---

## PIR Cadence

| Severity | PIR Required? | Deadline |
|----------|---------------|----------|
| **SEV1** | Mandatory | Within 3 business days |
| **SEV2** | Mandatory | Within 3 business days |
| **SEV3** | Optional | Within 1 week if conducted |
| **SEV4** | Not required | — |

### Review Process

- PIR author drafts the document within the deadline
- Team reviews in a 30-minute blameless meeting
- Action items are tracked to completion
- **Monthly review:** All open action items from past PIRs are reviewed on the first Monday of each month
