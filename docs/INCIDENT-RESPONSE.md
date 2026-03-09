# Incident Response Runbook

## Purpose and Scope

This runbook defines DualStack's incident response process, covering the full
lifecycle from detection through post-incident review. It applies to all
production incidents affecting service availability, data integrity, or security.

**Audience:** Engineering team, on-call responders, incident commanders.

---

## Severity Levels

| Level | Name | Description | Response Time | Acknowledge | Update Cadence |
|-------|------|-------------|---------------|-------------|----------------|
| **SEV1** | Critical | Service down or data loss | 15 minutes | 15 min | Every 30 min |
| **SEV2** | Major | Significant degradation, partial outage | 30 minutes | 30 min | Every 1 hour |
| **SEV3** | Minor | Limited impact, workaround available | 4 hours | 4 hours | Daily |
| **SEV4** | Low | Cosmetic, no user impact | Next business day | 1 business day | As needed |

### Severity Examples

- **SEV1:** API returning 500 for all requests; database unreachable; authentication service completely down; data breach confirmed
- **SEV2:** Error rate above 10%; specific endpoints failing; payment processing degraded; response times >5s
- **SEV3:** Single non-critical endpoint returning errors; background job failures; minor UI rendering issues
- **SEV4:** Cosmetic bugs; documentation errors; non-user-facing log noise

---

## Detection

Incidents are detected through one or more of these channels:

### Automated Alerting (Primary)

Grafana alert rules (provisioned in `monitoring/grafana/provisioning/alerting/`):

| Alert | Threshold | Severity |
|-------|-----------|----------|
| High Error Rate | >5% 5xx responses over 5 min | Critical |
| High Auth Failure Rate | >10 auth failures (401/403) per minute | Warning |
| High P99 Latency | P99 >2 seconds over 5 min | Warning |

Prometheus alert rules (`monitoring/prometheus/alerts/`):

| Alert | Threshold | Severity |
|-------|-----------|----------|
| APIDown | No requests for 2 min | Critical |
| DatabasePoolExhausted | All connections in use | Critical |
| APIHighLatency | P95 >2s for 5 min | Warning |
| BackgroundJobFailure | Any job failing | Warning |

### Other Sources

- **Health checks:** `GET /health` endpoint monitored externally
- **User reports:** Support tickets or direct reports
- **Error tracking:** Application logs via structured logging (structlog)
- **Deployment monitoring:** CI/CD pipeline failure notifications

---

## Triage Process

### Step 1: Acknowledge

1. Acknowledge the alert within the response time for the suspected severity level
2. Join the incident Slack channel (or create one: `#incident-YYYY-MM-DD-brief`)

### Step 2: Assign Incident Commander

The first responder becomes incident commander (IC) unless they delegate. The IC:
- Owns the incident until resolution or handoff
- Coordinates communication
- Makes decisions on escalation

### Step 3: Assess Severity

1. Check Grafana dashboards for scope of impact
2. Determine how many users/endpoints are affected
3. Assign severity level per the table above
4. Escalate if severity is higher than initially assessed

### Step 4: Determine Blast Radius

- Which endpoints/services are affected?
- Is data integrity at risk?
- Are payments or billing affected?
- How many users are impacted?

---

## Communication Templates

### Internal Notification

```
INCIDENT: [SEV{1-4}] {Brief description}
Status: INVESTIGATING / IDENTIFIED / MONITORING / RESOLVED
Impact: {Description of user impact}
IC: {Name}
Channel: #incident-{date}-{slug}
Dashboard: {Grafana dashboard URL}
```

### Status Page / Customer-Facing Update

```
[Investigating] We are aware of {issue description} affecting {service area}.
Our team is actively investigating. We will provide updates as we learn more.

Last updated: {timestamp}
```

### Escalation Notification

```
ESCALATION: [SEV{1-2}] {Brief description}
Current status: {What we know so far}
Duration: {Time since detection}
Actions taken: {What has been tried}
Need: {What is needed from the escalation target}
Contact: {IC name and channel}
```

### Resolution Notification

```
RESOLVED: [SEV{1-4}] {Brief description}
Duration: {Total incident duration}
Root cause: {One-line summary}
Impact: {Summary of user impact}
Follow-up: Post-incident review scheduled for {date}
```

---

## Resolution Steps

### 1. Isolate

- If a specific deployment caused the issue, consider rollback (see below)
- If a specific endpoint is failing, evaluate disabling it temporarily
- If an external dependency is down, activate circuit breakers or fallbacks

### 2. Diagnose

- Check Grafana dashboards: System Health, Database, Background Jobs
- Check application logs: `docker logs dualstack-api --tail 200`
- Check Prometheus metrics: query specific metric at `localhost:9090`
- Check recent deployments: `git log --oneline -10`
- Check database connectivity: `GET /health` endpoint

### 3. Fix or Rollback

**Fix forward** (preferred when the fix is quick and clear):
- Apply the fix, push, and deploy
- Monitor metrics for recovery

**Rollback** (when the fix is unclear or will take time):
```bash
# Identify the last known good commit
git log --oneline -10

# Deploy previous version
git revert HEAD
git push origin main
```

### 4. Verify

- Confirm error rate returns to normal (<1%)
- Confirm latency returns to baseline
- Confirm affected endpoints return 200
- Monitor for at least 15 minutes after fix

### 5. Monitor

- Keep the incident channel open for 1 hour after resolution
- Watch for regression in Grafana dashboards
- Confirm no related alerts fire

---

## Specific Incident Runbooks

### High Error Rate (>5%)

**Detection:** Grafana alert "High Error Rate" or Prometheus "APIHighErrorRate"

1. Open System Health dashboard, check "HTTP Request Rate by Status Code" panel
2. Identify which endpoints are returning 5xx: check "HTTP Request Rate by Endpoint"
3. Check application logs for stack traces:
   ```bash
   docker logs dualstack-api --tail 500 | grep -i error
   ```
4. If caused by a recent deployment, rollback
5. If caused by database issues, check Database dashboard and connection pool metrics
6. If caused by an external service (Stripe, Clerk), check external API call rate panel

### Authentication Service Failure

**Detection:** Grafana alert "High Auth Failure Rate" (>10 401/403 per minute)

1. Check if Clerk is experiencing an outage (status.clerk.com)
2. Check if JWKS endpoint is reachable:
   ```bash
   curl -s https://{CLERK_DOMAIN}/.well-known/jwks.json | head -c 200
   ```
3. Check if the issue is specific users or all users (check endpoint breakdown)
4. If Clerk is down:
   - Monitor Clerk status page
   - Consider enabling a maintenance page
5. If JWKS cache is stale, restart the API service:
   ```bash
   docker restart dualstack-api
   ```

### Database Connectivity Issues

**Detection:** Prometheus "DatabasePoolExhausted" or health check failures

1. Check Database dashboard: connection pool utilization, query latency
2. Check if the database is reachable:
   ```bash
   docker exec dualstack-api python -c "from app.core.database import engine; print('OK')"
   ```
3. Check for long-running queries or locks
4. If pool is exhausted:
   - Check for connection leaks (queries not releasing connections)
   - Restart the API to reset the pool as a temporary measure
5. If the database file is corrupted (SQLite):
   - Stop the API
   - Restore from the most recent backup
   - Restart and verify

### Deployment Failure / Rollback

**Detection:** CI/CD pipeline failure or post-deploy error spike

1. Check the deployment logs in CI/CD
2. If the deployment succeeded but errors spiked:
   ```bash
   git log --oneline -5  # identify the deployed commit
   git revert HEAD        # revert the change
   git push origin main   # trigger redeploy
   ```
3. If the deployment failed mid-way:
   - Check which services were updated
   - Manually redeploy the last known good version
4. If database migrations failed:
   - Do NOT retry automatically
   - Assess the migration state manually
   - Apply a downgrade migration if available

---

## Post-Incident Review

Schedule a post-incident review (PIR) within 3 business days for SEV1/SEV2
incidents. SEV3 incidents are reviewed at the team's discretion.

### Post-Incident Review Template

```markdown
# Post-Incident Review: {Incident Title}

**Date:** {Date of incident}
**Severity:** SEV{1-4}
**Duration:** {Start time} to {End time} ({total duration})
**IC:** {Incident Commander}
**Author:** {PIR author}

## Timeline

| Time (UTC) | Event |
|------------|-------|
| HH:MM | Alert fired / incident detected |
| HH:MM | Incident acknowledged |
| HH:MM | Root cause identified |
| HH:MM | Fix deployed |
| HH:MM | Incident resolved |

## Root Cause

{Detailed explanation of what caused the incident.}

## Impact

- **Users affected:** {number or percentage}
- **Duration of impact:** {time}
- **Data loss:** {yes/no, details}
- **Revenue impact:** {if applicable}

## What Went Well

- {Thing that worked}
- {Thing that worked}

## What Could Be Improved

- {Area for improvement}
- {Area for improvement}

## Action Items

| Action | Owner | Due Date | Priority |
|--------|-------|----------|----------|
| {Description} | {Name} | {Date} | P{0-2} |
| {Description} | {Name} | {Date} | P{0-2} |

## Lessons Learned

{Key takeaways that should inform future incident response or system design.}
```

---

## On-Call Rotation

> **Placeholder:** Define on-call rotation schedule and escalation paths here
> once the team is established. See T15.5 for on-call rotation implementation.

### Escalation Path

1. **Primary on-call:** First responder for all alerts
2. **Secondary on-call:** Backup if primary is unavailable (15 min no-response)
3. **Engineering lead:** Escalation for SEV1 incidents or if on-call needs support
4. **Management:** Notification for SEV1 incidents lasting >1 hour
