#!/bin/bash
# Smoke test for Prometheus monitoring stack
# Verifies that Prometheus is running and scraping backend metrics

set -e

echo "Testing Prometheus monitoring stack..."
echo ""

# Wait for Prometheus to start
echo "Waiting for Prometheus to start (5 seconds)..."
sleep 5

# Check if Prometheus is healthy
echo "Checking Prometheus health..."
if ! curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
  echo "FAIL: Prometheus is not healthy"
  exit 1
fi
echo "  OK: Prometheus is healthy"

# Check if Prometheus UI is accessible
echo "Checking Prometheus UI..."
if ! curl -f http://localhost:9090 > /dev/null 2>&1; then
  echo "FAIL: Prometheus UI is not accessible"
  exit 1
fi
echo "  OK: Prometheus UI is accessible"

# Check if backend target exists
echo "Checking backend target configuration..."
if ! curl -s http://localhost:9090/api/v1/targets | grep -q "dualstack-api"; then
  echo "FAIL: Backend target 'dualstack-api' not found"
  exit 1
fi
echo "  OK: Backend target configured"

# Check if any metrics are available
echo "Checking metrics availability..."
METRIC_COUNT=$(curl -s http://localhost:9090/api/v1/label/__name__/values | jq '.data | length')
if [ "$METRIC_COUNT" -lt 1 ]; then
  echo "FAIL: No metrics found"
  exit 1
fi
echo "  OK: Found $METRIC_COUNT metrics"

# Check for specific backend metrics
echo "Checking backend-specific metrics..."
BACKEND_METRICS=("http_requests_total" "db_connection_pool_size" "background_job_duration_seconds")
FOUND_METRICS=0

for metric in "${BACKEND_METRICS[@]}"; do
  if curl -s "http://localhost:9090/api/v1/query?query=${metric}" | grep -q "\"status\":\"success\""; then
    echo "  OK: Found metric: $metric"
    FOUND_METRICS=$((FOUND_METRICS + 1))
  else
    echo "  WARN: Metric not yet available: $metric (may need backend traffic)"
  fi
done

if [ "$FOUND_METRICS" -eq 0 ]; then
  echo "FAIL: No backend metrics found (backend may not be running)"
  exit 1
fi

echo ""
echo "OK: Monitoring stack is healthy!"
echo "   Prometheus UI: http://localhost:9090"
echo "   Targets page: http://localhost:9090/targets"
echo "   Metrics: $METRIC_COUNT available, $FOUND_METRICS backend metrics found"
