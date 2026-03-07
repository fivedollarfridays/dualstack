# DualStack Monitoring Stack

Prometheus-based monitoring for the DualStack backend. Collects and stores metrics from the FastAPI application for observability and alerting.

## Overview

This monitoring stack includes:

- **Prometheus** - Metrics collection and storage
- **Grafana** - Visualization dashboards
- **Alertmanager** - Alert routing and notification
- **Metrics Endpoint** - Backend exposes `/metrics` in Prometheus format
- **Persistent Storage** - Metrics retained for 15 days (configurable)
- **Health Checks** - Automatic service monitoring
- **Pre-built Dashboards** - 3 comprehensive dashboards for system observability

## Quick Start

### Development

Start the monitoring stack for local development:

```bash
cd monitoring
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Access services:
- **Prometheus UI**: http://localhost:9090
- **Grafana**: http://localhost:3001 (default credentials: admin/admin)

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

### Grafana Password

The default Grafana admin password is `admin`. Override it by setting the `GRAFANA_ADMIN_PASSWORD` environment variable before starting the stack:

```bash
GRAFANA_ADMIN_PASSWORD=your-secure-password docker-compose up -d
```

### Metrics API Key

If the backend has `METRICS_API_KEY` set, Prometheus needs the same key to scrape metrics. Edit `prometheus/prometheus.prod.yml` and uncomment the `authorization` section with your key.

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

### Background Job Metrics
- `background_job_duration_seconds` - Job execution duration
- `background_job_executions_total` - Total executions by job and status
- `background_job_failures_total` - Failures by job and error type
- `background_job_last_success_timestamp` - Last successful run timestamp

### External API Metrics
- `external_api_calls_total` - External API calls by service and status

## Accessing Grafana

### Grafana UI

Open http://localhost:3001 in your browser.

**Default Credentials:**
- Username: `admin`
- Password: `admin` (change via `GRAFANA_ADMIN_PASSWORD` env var)

You will be prompted to change the password on first login.

### Available Dashboards

The monitoring stack includes 3 pre-configured dashboards:

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

#### 2. Database Dashboard
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

#### 3. Background Jobs Dashboard
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

**Use Cases:**
- Monitor background job health
- Track job execution patterns
- Identify failing jobs and error types
- Analyze job performance and duration trends

### Using Grafana

**Time Range Selection:**
- Use the time picker in the top right to adjust the time window
- Common ranges: Last 1h, Last 6h, Last 24h, Last 7d

**Refresh Rate:**
- Dashboards auto-refresh every 30 seconds
- Adjust refresh rate in the top right dropdown

## Accessing Prometheus

### Prometheus UI

Open http://localhost:9090 in your browser.

**Key Pages:**
- **Graph** - Query and visualize metrics
- **Targets** - View scrape target health
- **Alerts** - View active alerts
- **Configuration** - View current configuration

### Example Queries

```promql
# Total HTTP requests in the last 5 minutes
sum(rate(http_requests_total[5m]))

# Database connection pool utilization
db_connection_pool_checked_out / db_connection_pool_size

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

#### Warning (P1) - Action Required Soon
- **APIHighLatency** - P95 latency >2s for 5 minutes
- **APIHighLatencyByEndpoint** - Slow specific endpoint
- **BackgroundJobFailure** - Any background job failing
- **DatabaseSlowQueries** - P95 query time >1s for 5 minutes
- **DatabaseSlowQueriesByOperation** - Slow specific operations

#### Info (P2) - Awareness
- **DatabasePoolHighUtilization** - >80% pool usage for 10 minutes
- **ExternalAPIRateHigh** - High external API usage
- **BackgroundJobSlowExecution** - Jobs running slow (>30s avg)

### Notification Channels

**Development:**
- Console logging (stdout)
- Local webhook (for testing)

**Production (configure in `alertmanager/alertmanager.yml`):**
- **Critical alerts**: PagerDuty, Slack, Email
- **Warning alerts**: Slack, Email
- **Info alerts**: Slack

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

## Troubleshooting

### Prometheus Can't Scrape Backend

**Symptom:** Target shows as "DOWN" in http://localhost:9090/targets

**Solutions:**

1. **Development:** Make sure backend is running on localhost:8000
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Docker:** Make sure backend is on the same network
   ```bash
   docker network ls
   docker network inspect dualstack-backend-network
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
   docker logs dualstack-prometheus
   ```

### Data Not Persisting

**Symptom:** Metrics lost after restart

**Solutions:**

1. Check volume is mounted:
   ```bash
   docker volume ls | grep prometheus
   ```

2. Verify data directory permissions:
   ```bash
   docker exec dualstack-prometheus ls -la /prometheus
   ```

## Production Deployment

### Prerequisites

1. Backend running with `/metrics` endpoint exposed
2. Docker and Docker Compose installed
3. Persistent volume storage configured

### Deployment Steps

1. **Configure backend network:**
   ```bash
   docker network create dualstack-backend-network
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

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
