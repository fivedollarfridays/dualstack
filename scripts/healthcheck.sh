#!/usr/bin/env bash
# Health check script for DualStack backend.
# Checks /health/live and /health/ready endpoints.
# Exits non-zero on any failure. Usable in cron jobs or external monitoring.
#
# Usage:
#   ./scripts/healthcheck.sh                         # default: http://localhost:8000
#   ./scripts/healthcheck.sh --url https://app.example.com

set -euo pipefail

BASE_URL="http://localhost:8000"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)
      BASE_URL="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

# Remove trailing slash
BASE_URL="${BASE_URL%/}"

check_endpoint() {
  local endpoint="$1"
  local url="${BASE_URL}${endpoint}"
  local http_code

  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url")

  if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
    echo "OK: ${endpoint} (${http_code})"
  else
    echo "FAIL: ${endpoint} (${http_code})" >&2
    return 1
  fi
}

failed=0

check_endpoint "/health/live" || failed=1
check_endpoint "/health/ready" || failed=1

if [[ "$failed" -ne 0 ]]; then
  echo "Health check failed" >&2
  exit 1
fi

echo "All health checks passed"
