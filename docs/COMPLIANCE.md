# SOC2 Compliance Gap Analysis

## Overview

This document identifies SOC2 Trust Services Criteria gaps and provides a
remediation roadmap. DualStack currently addresses several security controls
but has gaps in monitoring, incident response, and backup strategy.

## Current Controls (Implemented)

| Control | Status | Implementation |
|---------|--------|----------------|
| Authentication | Done | Clerk JWT validation with JWKS |
| Authorization | Done | User-scoped data access (row-level) |
| Audit Logging | Done | `log_audit_event` on auth failures, webhooks, CRUD |
| Rate Limiting | Done | SlowAPI per-endpoint limits |
| Input Validation | Done | Pydantic schemas, Content-Length limits |
| Security Headers | Done | HSTS, nonce-based CSP, X-Frame-Options, etc. |
| Secrets Management | Done | Environment variables, no hardcoded secrets |
| Webhook Verification | Done | Stripe signature validation, empty-secret guard |
| Metrics Auth | Done | Bearer token auth on /metrics endpoint (production) |
| Database Access Control | Done | Frontend uses read-only scoped token, validated at startup |
| Monitoring Auth | Done | Prometheus UI basic-auth, Grafana-Prometheus auth configured |

## Gaps and Remediation

### CC7.1 — Monitoring and Detection

**Current state:** Prometheus metrics collection with Grafana dashboards.
Structured logging via structlog. Automated alerting configured.

**Status:** Partially addressed (P1 complete, P2 remaining)

**Addressed:**
- Grafana alert rules provisioned for error rate > 5%, auth failure
  spike > 10/min, and P99 latency > 2s
  (`monitoring/grafana/provisioning/alerting/`)
- Prometheus alert rules for API down, pool exhaustion, slow queries
  (`monitoring/prometheus/alerts/`)
- Contact point and notification policies configured

**Remaining gaps (P2):**
- ~~No centralized log aggregation for production~~ — Addressed: Fluent Bit
  collects Docker container logs and forwards to Loki for centralized storage
  and querying via Grafana (`monitoring/fluent-bit/`, Loki datasource provisioned)
- ~~No uptime monitoring or health check alerting~~ — Addressed: Prometheus
  uptime alert rules (`monitoring/prometheus/alerts/uptime.yml`), PagerDuty
  integration in Alertmanager, managed uptime service guide in
  `docs/MONITORING.md`, health check script (`scripts/healthcheck.sh`)

### CC7.2 — Incident Response

**Current state:** Incident response runbook documented.
See [`docs/INCIDENT-RESPONSE.md`](INCIDENT-RESPONSE.md).

**Status:** Partially addressed (P1 complete, P2 remaining)

**Addressed:**
- Incident response runbook with severity levels, detection, triage,
  communication templates, resolution steps, and specific runbooks
- Post-incident review template with timeline, root cause, impact, action items

**Remaining gaps (P2):**
- ~~On-call rotation and escalation policies~~ — Addressed: weekly rotation
  schedule, SEV1-SEV4 response SLAs, escalation matrix, handoff procedure
  defined in [`docs/ON-CALL.md`](ON-CALL.md)
- ~~Post-incident review cadence not yet enforced~~ — Addressed: PIR template
  with metadata, timeline, root cause analysis (5 Whys), action items, and
  lessons learned. Mandatory for SEV1/SEV2 within 3 business days, monthly
  action item review. See [`docs/PIR-TEMPLATE.md`](PIR-TEMPLATE.md)

### CC6.1 — Backup and Recovery

**Current state:** Automated backup script with documented RPO/RTO targets.
See [`docs/BACKUP-RECOVERY.md`](BACKUP-RECOVERY.md).

**Status:** Partially addressed (P1 complete, P2 remaining)

**Addressed:**
- RPO < 1 hour, RTO < 4 hours targets defined and documented
- Automated backup script (`scripts/backup.sh`) using `sqlite3 .backup`
  for consistent snapshots with retention policy
- Step-by-step restore procedure documented and tested
- PostgreSQL backup path documented for production deployments

**Remaining gaps (P2):**
- ~~Backup monitoring alerts (backup age, size anomaly)~~ — Addressed:
  Prometheus alert rules in `monitoring/prometheus/alerts/backup.yml`
  (BackupTooOld warning at 2h / critical at 6h, BackupSizeAnomaly at 50%
  deviation). Response procedures in `docs/BACKUP-RECOVERY.md`.
- ~~Quarterly restore-to-staging testing not yet scheduled~~ — Addressed:
  `scripts/restore.sh` with safety backup, integrity validation, and
  documented test procedure in `docs/BACKUP-RECOVERY.md`. Testing schedule
  defined (monthly manual, quarterly full restore, weekly integrity).
- Litestream continuous replication for near-zero RPO (enhancement)

## Priority Summary

| Priority | Items | Target |
|----------|-------|--------|
| P1 | ~~Alerting rules~~, ~~incident runbook~~, ~~backup strategy~~, ~~RPO/RTO~~ | Done |
| P2 | ~~Log aggregation~~, ~~uptime monitoring~~, ~~on-call~~, ~~restore testing~~, ~~backup alerts~~ | Post-launch |
