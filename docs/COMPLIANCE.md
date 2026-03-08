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
| Security Headers | Done | HSTS, CSP, X-Frame-Options, etc. |
| Secrets Management | Done | Environment variables, no hardcoded secrets |
| Webhook Verification | Done | Stripe signature validation, empty-secret guard |

## Gaps and Remediation

### CC7.1 — Monitoring and Detection

**Current state:** Prometheus metrics collection with Grafana dashboards.
Structured logging via structlog.

**Gaps:**
- No automated alerting rules for anomalous patterns (e.g., auth failure
  spikes, error rate thresholds)
- No centralized log aggregation for production (logs are container-local)
- No uptime monitoring or health check alerting

**Remediation:**
1. **P1:** Configure Grafana alert rules for error rate > 5%, auth failure
   spike > 10/min, and response latency P99 > 2s
2. **P2:** Add a log shipping sidecar (e.g., Fluent Bit) to forward logs to a
   centralized service (e.g., Datadog, Loki, CloudWatch)
3. **P2:** Set up uptime monitoring on the `/health` endpoint with PagerDuty
   or Opsgenie integration

### CC7.2 — Incident Response

**Current state:** No formal incident response plan.

**Gaps:**
- No documented incident response runbook
- No on-call rotation or escalation path
- No post-incident review process

**Remediation:**
1. **P1:** Create an incident response runbook covering: detection, triage,
   containment, resolution, and communication
2. **P2:** Define on-call rotation and escalation policies
3. **P2:** Establish a post-incident review template and cadence

### CC6.1 — Backup and Recovery

**Current state:** SQLite database with no automated backup strategy.

**Gaps:**
- No automated database backups
- No documented recovery procedure
- No tested restore process
- No defined RPO/RTO targets

**Remediation:**
1. **P1:** Define RPO (Recovery Point Objective) and RTO (Recovery Time
   Objective) targets
2. **P1:** Implement automated database backups (Turso handles this if using
   their hosted service; for self-hosted SQLite, use Litestream or cron-based
   snapshots)
3. **P2:** Document and test the restore procedure
4. **P2:** Set up backup monitoring alerts (backup age, backup size anomalies)

## Priority Summary

| Priority | Items | Target |
|----------|-------|--------|
| P1 | Alerting rules, incident runbook, backup strategy, RPO/RTO | Pre-launch |
| P2 | Log aggregation, uptime monitoring, on-call, restore testing | Post-launch |
