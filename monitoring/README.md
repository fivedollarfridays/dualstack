# Companion AI Monitoring Stack

Prometheus-based monitoring for the Companion AI backend. Collects and stores metrics from the FastAPI application for observability and alerting.

## Overview

This monitoring stack includes:

- **Prometheus** - Metrics collection and storage
- **Grafana** - Visualization dashboards
- **Metrics Endpoint** - Backend exposes `/metrics` in Prometheus format
- **Persistent Storage** - Metrics retained for 15 days (configurable)
- **Health Checks** - Automatic service monitoring
- **Pre-built Dashboards** - 4 comprehensive dashboards for system observability

## Quick Start

### Development

Start the monitoring stack for local development:

```bash
cd monitoring
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Access services:
- **Prometheus UI**: http://localhost:9090
- **Grafana**: http://localhost:3000 (default credentials: admin/admin)

### Production

Start the monitoring stack for production:

```bash
cd monitoring
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Stop the Stack

```bash
cd monitoring
docker-compose down
```

### Remove All Data

```bash
cd monitoring
docker-compose down -v  # Removes volumes
```

## Configuration

### Environment-Specific Settings

| Setting | Development | Production |
|---------|-------------|------------|
| Scrape Interval | 15s | 30s |
| Retention Period | 7 days | 30 days |
| Backend Target | localhost:8000 | backend:8000 |
| Network Mode | host | bridge |

### Files

- `prometheus/prometheus.yml` - Base configuration
- `prometheus/prometheus.dev.yml` - Development overrides
- `prometheus/prometheus.prod.yml` - Production overrides
- `docker-compose.yml` - Base Docker Compose
- `docker-compose.dev.yml` - Development overrides
- `docker-compose.prod.yml` - Production overrides

## Available Metrics

The backend exposes the following metric categories:

### HTTP Metrics
- `http_requests_total` - Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds` - Request duration histogram

### Database Metrics
- `db_operations_total` - Database operations by table and status
- `db_connection_pool_size` - Total connections in pool
- `db_connection_pool_checked_out` - Active connections
- `db_connection_pool_overflow` - Overflow connections
- `db_query_duration_seconds` - Query execution time by operation

### Video Generation Metrics
- `video_requests_total` - Video generation requests by type and status
- `video_jobs_pending` - Current pending video jobs
- `video_jobs_processing` - Current processing video jobs
- `video_jobs_completed_total` - Completed jobs by video type
- `video_jobs_failed_total` - Failed jobs by type and error
- `video_retry_attempts_total` - Retry attempts by error type
- `video_r2_upload_errors_total` - R2 upload failures
- `video_generation_duration_seconds` - Generation duration histogram

### Background Job Metrics
- `background_job_duration_seconds` - Job execution duration
- `background_job_executions_total` - Total executions by job and status
- `background_job_failures_total` - Failures by job and error type
- `background_job_last_success_timestamp` - Last successful run timestamp

### External API Metrics
- `external_api_calls_total` - External API calls by service and status

## Accessing Grafana

### Grafana UI

Open http://localhost:3000 in your browser.

**Default Credentials:**
- Username: `admin`
- Password: `admin`

You will be prompted to change the password on first login.

### Available Dashboards

The monitoring stack includes 4 pre-configured dashboards:

#### 1. System Health Dashboard
Monitors overall backend health and HTTP performance.

**Panels:**
- Request rate (requests/sec)
- Error rate (%)
- P95 latency (ms)
- Total requests (1h)
- HTTP request rate by endpoint
- HTTP request rate by status code
- Request duration percentiles (p50, p95, p99)
- External API call rate

**Use Cases:**
- Identify traffic spikes and patterns
- Monitor API endpoint performance
- Track error rates by endpoint and status code
- Detect latency degradation

#### 2. Video Generation Dashboard
Monitors video generation jobs and performance.

**Panels:**
- Pending jobs count
- Processing jobs count
- Completion rate (jobs/min)
- Failure rate (%)
- Video requests by type (clip/talking_head)
- Job queue depth (pending/processing)
- Job completion/failure rate
- Video generation duration
- Failures by error type
- Retry attempts by error
- R2 upload errors (1h)

**Use Cases:**
- Monitor video generation pipeline health
- Identify bottlenecks in job processing
- Track failure patterns and error types
- Analyze generation performance by video type

#### 3. Database Dashboard
Monitors database connection pool and query performance.

**Panels:**
- Connection pool utilization (gauge)
- Pool size, checked out connections, overflow
- Query rate (queries/sec)
- P95 query latency (ms)
- Slow queries (>1s) per minute
- Connection pool metrics over time
- Query rate by operation (SELECT/INSERT/UPDATE/DELETE)
- Query duration by operation (P95)
- Database operations rate
- Query duration heatmap

**Use Cases:**
- Monitor connection pool exhaustion
- Identify slow queries
- Track query patterns by operation type
- Detect database performance degradation

#### 4. Background Jobs Dashboard
Monitors background job execution and performance.

**Panels:**
- Total job executions (1h)
- Success rate (%)
- Average job duration (sec)
- Total failures (1h)
- Job execution rate by job name
- Success vs failure rate
- Job duration by job name
- Job duration percentiles (p50, p95, p99)
- Failures by error type
- Last successful run by job (table)
- Individual job duration graphs (video_status_check, proactive_check, surprise_evaluation)

**Use Cases:**
- Monitor background job health
- Track job execution patterns
- Identify failing jobs and error types
- Analyze job performance and duration trends

### Using Grafana

**Time Range Selection:**
- Use the time picker in the top right to adjust the time window
- Common ranges: Last 1h, Last 6h, Last 24h, Last 7d
- Set custom ranges for specific time periods

**Refresh Rate:**
- Dashboards auto-refresh every 30 seconds
- Adjust refresh rate in the top right dropdown

**Panel Interactions:**
- Click panel titles to view full-screen
- Hover over graphs to see values
- Click legend items to show/hide series
- Use zoom tools to focus on specific time ranges

**Filtering:**
- Use template variables (when available) to filter by specific metrics
- Use the search bar to find specific panels

**Sharing:**
- Click share icon to get direct links to dashboards
- Export dashboards as JSON for backup or sharing

## Accessing Prometheus

### Prometheus UI

Open http://localhost:9090 in your browser.

**Key Pages:**
- **Graph** - Query and visualize metrics
- **Targets** - View scrape target health
- **Alerts** - View active alerts (after adding alert rules)
- **Configuration** - View current configuration

### Example Queries

```promql
# Total HTTP requests in the last 5 minutes
sum(rate(http_requests_total[5m]))

# Database connection pool utilization
db_connection_pool_checked_out / db_connection_pool_size

# Video job failure rate
rate(video_jobs_failed_total[5m]) / rate(video_requests_total[5m])

# Background job duration (95th percentile)
histogram_quantile(0.95, rate(background_job_duration_seconds_bucket[5m]))

# Slow queries (>1 second)
rate(db_query_duration_seconds_bucket{le="1"}[5m])
```

## Alerting

### Alert Configuration

The monitoring stack includes Prometheus Alertmanager for alert routing and notification management.

**Access Alertmanager UI**: http://localhost:9093

### Alert Severity Levels

Alerts are organized into three severity levels:

#### Critical (P0) - Immediate Action Required
- **APIHighErrorRate** - >5% 5xx errors for 5 minutes
- **APIDown** - No requests received for 2 minutes
- **DatabasePoolExhausted** - All connections in use
- **VideoJobFailureSpike** - >10% failure rate for 10 minutes

**Response**: Page on-call engineer immediately

#### Warning (P1) - Action Required Soon
- **APIHighLatency** - P95 latency >2s for 5 minutes
- **APIHighLatencyByEndpoint** - Slow specific endpoint
- **VideoJobsStuckPending** - >100 jobs pending for 15 minutes
- **BackgroundJobFailure** - Any background job failing
- **DatabaseSlowQueries** - P95 query time >1s for 5 minutes
- **DatabaseSlowQueriesByOperation** - Slow specific operations

**Response**: Investigate within 30 minutes

#### Info (P2) - Awareness
- **DatabasePoolHighUtilization** - >80% pool usage for 10 minutes
- **VideoGenerationRateHigh** - High request rate
- **ExternalAPIRateHigh** - High external API usage
- **BackgroundJobSlowExecution** - Jobs running slow (>30s avg)

**Response**: Monitor and plan optimization

### Alert Runbooks

Each alert includes a runbook link with troubleshooting steps:

- **APIHighErrorRate**: Check application logs, recent deployments, external service status
- **APIDown**: Verify backend is running, check network connectivity, review container logs
- **DatabasePoolExhausted**: Check for connection leaks, increase pool size, review slow queries
- **VideoJobFailureSpike**: Check external API status, review job errors, verify R2 connectivity
- **APIHighLatency**: Profile slow endpoints, check database queries, review resource usage
- **VideoJobsStuckPending**: Check job processor status, review queue depth, verify worker capacity
- **BackgroundJobFailure**: Review job logs, check dependencies, verify configuration
- **DatabaseSlowQueries**: Identify slow queries, add indexes, optimize query patterns

### Silencing Alerts

To temporarily silence an alert:

1. Go to Alertmanager UI: http://localhost:9093
2. Click on the alert
3. Click "Silence"
4. Set duration and reason
5. Click "Create"

Silences are useful during:
- Planned maintenance
- Known issues being worked on
- Testing/development

### Notification Channels

**Development:**
- Console logging (stdout)
- Local webhook (for testing)

**Production (configure in `alertmanager.yml`):**
- **Critical alerts**:
  - PagerDuty (24/7 on-call)
  - Slack #alerts channel
  - Email to on-call team

- **Warning alerts**:
  - Slack #monitoring channel
  - Email to team

- **Info alerts**:
  - Slack #monitoring-info channel

### Alert Grouping and Deduplication

Alertmanager groups related alerts together to reduce noise:

- **Group by**: alertname, severity, component
- **Group wait**: 10s (critical), 30s (warning), 5m (info)
- **Repeat interval**: 5m (critical), 30m (warning), 2h (info)

**Inhibition rules** prevent redundant alerts:
- Critical alerts suppress warnings for same alert
- Warnings suppress info alerts for same alert
- APIDown suppresses all other API alerts

## Testing

### Smoke Test

Run the smoke test to verify the monitoring stack:

```bash
cd monitoring
./scripts/smoke-test.sh
```

### Alert Testing

Test alert configuration:

```bash
cd monitoring
./scripts/test-alerts.sh
```

Expected output:
```
🔍 Testing Prometheus alert configuration...

✓ Checking Prometheus health...
  ✅ Prometheus is healthy
✓ Checking Alertmanager health...
  ✅ Alertmanager is healthy
✓ Reloading alert rules...
  ✅ Alert rules reloaded
✓ Checking loaded alert rules...
  ✅ Alert rules loaded (3 groups)
  ✅ Total alert rules: 14

📋 Alert groups:
  - critical_alerts: 4 rules
  - warning_alerts: 6 rules
  - info_alerts: 4 rules

✓ Checking for firing alerts...
  📊 Firing alerts: 0
  📊 Pending alerts: 0

✓ Checking Alertmanager configuration...
  ✅ Alertmanager receivers configured: 4

✅ Alert configuration test complete!
```

### Triggering Test Alerts

To verify alerts fire correctly:

1. **APIDown**: Stop the backend
   ```bash
   docker stop backend-container
   # Wait 2 minutes, check http://localhost:9090/alerts
   ```

2. **APIHighErrorRate**: Generate 5xx errors
   ```bash
   # Make requests that cause errors
   for i in {1..100}; do curl http://localhost:8000/nonexistent; done
   ```

3. **DatabaseSlowQueries**: Run slow queries
   ```bash
   # Execute queries with artificial delays
   ```

4. **VideoJobsStuckPending**: Create many video jobs without processing

Expected output:
```
🔍 Testing Prometheus monitoring stack...

⏳ Waiting for Prometheus to start (5 seconds)...
✓ Checking Prometheus health...
  ✅ Prometheus is healthy
✓ Checking Prometheus UI...
  ✅ Prometheus UI is accessible
✓ Checking backend target configuration...
  ✅ Backend target configured
✓ Checking metrics availability...
  ✅ Found 50 metrics
✓ Checking backend-specific metrics...
  ✅ Found metric: http_requests_total
  ✅ Found metric: video_requests_total
  ✅ Found metric: db_connection_pool_size
  ✅ Found metric: background_job_duration_seconds

✅ Monitoring stack is healthy!
   📊 Prometheus UI: http://localhost:9090
   🎯 Targets page: http://localhost:9090/targets
   📈 Metrics: 50 available, 4 backend metrics found
```

## Troubleshooting

### Prometheus Can't Scrape Backend

**Symptom:** Target shows as "DOWN" in http://localhost:9090/targets

**Solutions:**

1. **Development:** Make sure backend is running on localhost:8000
   ```bash
   # In backend directory
   uvicorn app.main:app --reload
   ```

2. **Docker:** Make sure backend is on the same network
   ```bash
   # Check networks
   docker network ls

   # Inspect network
   docker network inspect companion-backend-network
   ```

3. **Check backend /metrics endpoint**
   ```bash
   curl http://localhost:8000/metrics
   ```

### No Metrics Data

**Symptom:** Queries return no results

**Solutions:**

1. Wait a few scrape intervals (30-60 seconds)
2. Generate some backend traffic (make API requests)
3. Check Prometheus logs:
   ```bash
   docker logs companion-prometheus
   ```

### Prometheus Container Won't Start

**Symptom:** `docker-compose up` fails

**Solutions:**

1. Check configuration syntax:
   ```bash
   docker run --rm -v $(pwd)/prometheus:/etc/prometheus prom/prometheus:latest \
     promtool check config /etc/prometheus/prometheus.yml
   ```

2. Check file permissions:
   ```bash
   ls -la prometheus/
   ```

3. View container logs:
   ```bash
   docker-compose logs prometheus
   ```

### Data Not Persisting

**Symptom:** Metrics lost after restart

**Solutions:**

1. Check volume is mounted:
   ```bash
   docker volume ls | grep prometheus
   ```

2. Inspect volume:
   ```bash
   docker volume inspect monitoring_prometheus-data
   ```

3. Verify data directory permissions inside container:
   ```bash
   docker exec companion-prometheus ls -la /prometheus
   ```

## Production Deployment

### Prerequisites

1. Backend running with `/metrics` endpoint exposed
2. Docker and Docker Compose installed
3. Persistent volume storage configured

### Deployment Steps

1. **Configure backend network:**
   ```bash
   docker network create companion-backend-network
   ```

2. **Deploy monitoring stack:**
   ```bash
   cd monitoring
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

3. **Verify deployment:**
   ```bash
   ./scripts/smoke-test.sh
   ```

4. **Set up external access (optional):**
   - Configure reverse proxy (nginx/traefik)
   - Add authentication (Prometheus doesn't have built-in auth)
   - Enable TLS

### Cloud-Specific Notes

#### AWS ECS/Fargate
- Use EFS for persistent storage
- Configure service discovery for backend target
- Use Application Load Balancer for ingress

#### Google Cloud Run
- Use Cloud Storage for persistent storage
- Configure VPC connector for backend access
- Use Cloud Load Balancing for ingress

#### Kubernetes
- Use PersistentVolumeClaim for storage
- Use Service discovery for backend target
- Use Ingress for external access

### Security Considerations

1. **Authentication:** Prometheus has no built-in auth. Use:
   - Reverse proxy with basic auth (nginx, traefik)
   - OAuth2 proxy
   - VPN/private network

2. **Network Isolation:**
   - Keep Prometheus on private network
   - Only expose through secure gateway
   - Use network policies in Kubernetes

3. **Data Retention:**
   - Balance retention vs storage costs
   - Consider using remote storage (Thanos, Cortex)

## Next Steps

1. **Add Grafana** (T-MON.5) - Visualization dashboards
2. **Configure Alert Rules** (T-MON.6) - Alerting on critical conditions
3. **Add Alertmanager** - Route alerts to Slack/PagerDuty
4. **Set up Remote Storage** - Long-term metrics retention

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

## Support

For issues or questions:
- Check troubleshooting section above
- Review Prometheus logs: `docker logs companion-prometheus`
- Verify backend logs for metric export errors
