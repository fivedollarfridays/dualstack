# Monitoring Guide

Comprehensive guide to DualStack's monitoring, uptime monitoring, and alerting infrastructure.

## Architecture

```
Backend (/metrics) → Prometheus → Grafana (dashboards)
                   → Alertmanager → PagerDuty / Slack
Docker containers  → Fluent Bit → Loki → Grafana (log explore)
External probe     → /health/live, /health/ready → Alert on failure
```

## Health Endpoints

The backend exposes health check endpoints used by infrastructure probes, uptime monitors, and Kubernetes:

| Endpoint | Purpose | Success | Failure |
|----------|---------|---------|---------|
| `/health/live` | Liveness — is the app running? | 200 `{"alive": true}` | N/A (always 200 if process is up) |
| `/health/ready` | Readiness — can the app serve traffic? | 200 `{"ready": true, ...}` | 503 `{"ready": false, ...}` |
| `/health` | General status | 200 `{"status": "healthy"}` | 200 `{"status": "degraded"}` |

**Use `/health/live`** for uptime monitors (is the process alive?).
**Use `/health/ready`** for load balancer health checks (can it handle requests?).

## Uptime Monitoring

External uptime monitoring detects outages from outside the infrastructure — a requirement for SOC2 CC7.1.

### Option A: Managed Uptime Service (Recommended)

Use a managed service for external monitoring with built-in alerting and status pages.

**UptimeRobot** (free tier available):

1. Sign up at https://uptimerobot.com
2. Add a new HTTP(s) monitor:
   - URL: `https://your-domain.com/health/live`
   - Monitoring interval: 5 minutes
   - Alert contacts: your email + PagerDuty integration
3. Add a second monitor for `/health/ready`
4. Configure a status page (optional) for public uptime visibility

**Better Uptime / BetterStack:**

1. Create a monitor at https://betterstack.com/better-uptime
2. URL: `https://your-domain.com/health/live`
3. Check period: 3 minutes
4. Connect to PagerDuty or on-call schedule

**Pingdom:**

1. Add an Uptime check in Pingdom dashboard
2. URL: `https://your-domain.com/health/live`
3. Check interval: 1 minute
4. Alert via PagerDuty integration

### Option B: Self-Hosted with Prometheus Blackbox Exporter

For teams preferring self-hosted monitoring:

1. Add blackbox_exporter to `monitoring/docker-compose.yml`
2. Configure probe targets for `/health/live` and `/health/ready`
3. Prometheus scrapes blackbox_exporter metrics
4. Alert rules in `monitoring/prometheus/alerts/uptime.yml` fire on probe failure

See `monitoring/prometheus/alerts/uptime.yml` for the pre-configured alert rules:
- **HealthLiveEndpointDown** (critical, 1m) — liveness probe failing
- **HealthReadyEndpointDown** (critical, 2m) — readiness probe failing
- **HealthEndpointSlow** (warning, 3m) — health check response >5s

### Standalone Health Check Script

A portable health check script is available for cron jobs or CI:

```bash
# Check against localhost
./scripts/healthcheck.sh

# Check against a custom URL
./scripts/healthcheck.sh --url https://app.example.com
```

Exits 0 on success, 1 on failure. Checks both `/health/live` and `/health/ready`.

## PagerDuty Integration

PagerDuty receives critical alerts from Alertmanager and pages the on-call engineer.

### Setup

1. **Create a PagerDuty service:**
   - Go to PagerDuty → Services → New Service
   - Name: `DualStack Production`
   - Escalation policy: select or create one
   - Integration: select "Prometheus Alertmanager"
   - Copy the **Integration Key** (also called Service Key or Routing Key)

2. **Configure the integration key:**
   ```bash
   export PAGERDUTY_SERVICE_KEY=<your-integration-key>
   envsubst < monitoring/alertmanager/alertmanager.yml > monitoring/alertmanager/alertmanager.resolved.yml
   ```

3. **Mount the resolved config** in your Docker Compose production override or set the environment variable in your deployment.

4. **Test the integration:**
   ```bash
   # Send a test alert via Alertmanager API
   curl -X POST http://localhost:9093/api/v2/alerts \
     -H "Content-Type: application/json" \
     -d '[{"labels":{"alertname":"TestAlert","severity":"critical"}}]'
   ```

### OpsGenie (Alternative)

Replace the `pagerduty_configs` block in `alertmanager.yml` with:

```yaml
opsgenie_configs:
  - api_key: '${OPSGENIE_API_KEY}'
    priority: 'P1'
```

Process with `envsubst` the same way.

## Alert Severity Mapping

| Severity | Action | Channel | Examples |
|----------|--------|---------|----------|
| **critical** | Page on-call immediately | PagerDuty | API down, health endpoint down, pool exhausted |
| **warning** | Notify within 30 minutes | Slack `#alerts-warning` | High latency, slow queries, job failures |
| **info** | Awareness, no action required | Slack `#alerts-info` | High pool utilization, slow background jobs |

## Alert Rules Reference

| File | Alerts |
|------|--------|
| `prometheus/alerts/critical.yml` | APIHighErrorRate, APIDown, DatabasePoolExhausted |
| `prometheus/alerts/warnings.yml` | APIHighLatency, BackgroundJobFailure, DatabaseSlowQueries, ... |
| `prometheus/alerts/info.yml` | DatabasePoolHighUtilization, ExternalAPIRateHigh, ... |
| `prometheus/alerts/uptime.yml` | HealthLiveEndpointDown, HealthReadyEndpointDown, HealthEndpointSlow |

## Grafana Alert Rules

Grafana-provisioned alerts are in `monitoring/grafana/provisioning/alerting/`:
- Error rate > 5% for 5 minutes
- Auth failure spike > 10/min for 3 minutes
- P99 latency > 2s for 5 minutes
