# On-Call Rotation and Escalation

Defines the on-call rotation schedule, response time SLAs, and escalation
policies for DualStack production incident response.

## On-Call Rotation Schedule

DualStack uses a **weekly rotation** with primary and secondary on-call roles.

### Roster Template

| Week Starting | Primary On-Call | Secondary On-Call |
|---------------|-----------------|-------------------|
| YYYY-MM-DD | Engineer A | Engineer B |
| YYYY-MM-DD | Engineer B | Engineer C |
| YYYY-MM-DD | Engineer C | Engineer A |

- **Rotation day:** Monday at 10:00 AM local time
- **Primary:** First responder for all alerts; triages and resolves incidents
- **Secondary:** Backup if primary is unavailable or incident requires additional support
- **Minimum roster size:** 3 engineers to allow adequate recovery time

### On-Call Responsibilities

The on-call engineer is expected to:

1. **Monitor alerts** — Watch PagerDuty/OpsGenie for incoming pages
2. **Acknowledge pages** — Acknowledge within the SLA for the alert severity
3. **Triage incidents** — Assess severity, determine scope and impact
4. **Communicate status** — Post updates in the incident channel per update cadence
5. **Resolve or escalate** — Fix the issue or escalate per the escalation matrix
6. **Document** — Log timeline entries during the incident for the PIR

## Response Time SLAs

| Severity | Acknowledge | Begin Triage | Update Cadence |
|----------|-------------|--------------|----------------|
| **SEV1** (Critical) | 5 min | 15 min | Every 30 min |
| **SEV2** (High) | 15 min | 30 min | Every 1 hour |
| **SEV3** (Medium) | 1 hour | 4 hours | Daily |
| **SEV4** (Low) | Next business day | Next business day | As needed |

### Severity Definitions

- **SEV1:** Complete service outage, data loss, or security breach
- **SEV2:** Significant degradation (>10% error rate, payment failures)
- **SEV3:** Limited impact with workaround available
- **SEV4:** Cosmetic issues, no user impact

## Escalation Matrix

| Severity | Step 1 | Step 2 (if unresolved) | Step 3 (if unresolved) |
|----------|--------|------------------------|------------------------|
| **SEV1** | Primary on-call (immediate) | Engineering lead (+15 min) | CTO (+30 min) |
| **SEV2** | Primary on-call (immediate) | Engineering lead (+30 min) | — |
| **SEV3** | Primary on-call (per SLA) | No auto-escalation | — |
| **SEV4** | Ticket queue | No page | — |

### Escalation Rules

- **Auto-escalation:** If the primary on-call does not acknowledge within the SLA, the alert automatically escalates to the secondary on-call
- **Manual escalation:** The on-call engineer can escalate at any time if the incident exceeds their expertise or requires broader coordination
- **Severity upgrade:** If an incident worsens (e.g., SEV3 becomes SEV2), re-route the alert through the escalation matrix for the new severity

## Handoff Procedure

When rotating on-call responsibilities:

1. **Outgoing on-call** prepares a handoff summary:
   - Open incidents and their current status
   - Known issues or degraded services
   - Upcoming deployments or maintenance windows
   - Any alerts that were silenced and why

2. **Handoff meeting** (15 min, Monday 10:00 AM):
   - Walk through the handoff summary
   - Review any recurring alerts from the past week
   - Confirm contact information and availability

3. **Incoming on-call** verifies:
   - PagerDuty/OpsGenie schedule shows them as primary
   - Notification channels are working (test page)
   - Access to monitoring dashboards and runbooks

## Tools

- **PagerDuty** or **OpsGenie** — Schedule management, alert routing, escalation policies
- **Grafana** — Monitoring dashboards (http://localhost:3001)
- **Alertmanager** — Alert routing configuration (`monitoring/alertmanager/alertmanager.yml`)
- **Incident Response Runbook** — [`docs/INCIDENT-RESPONSE.md`](INCIDENT-RESPONSE.md)
- **PIR Template** — [`docs/PIR-TEMPLATE.md`](PIR-TEMPLATE.md)
