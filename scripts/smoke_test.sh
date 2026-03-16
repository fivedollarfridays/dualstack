#!/usr/bin/env bash
# Smoke test for DualStack API.
# Verifies critical endpoints are reachable after deployment.
#
# Usage:
#   ./scripts/smoke_test.sh                              # default: http://localhost:8000
#   ./scripts/smoke_test.sh --url https://app.example.com
#   ./scripts/smoke_test.sh --help

set -euo pipefail

BASE_URL="http://localhost:8000"
PASS=0
FAIL=0

usage() {
  echo "Usage: $0 [--url BASE_URL]"
  echo ""
  echo "Options:"
  echo "  --url URL   Base URL to test (default: http://localhost:8000)"
  echo "  --help      Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0"
  echo "  $0 --url https://api.example.com"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)
      BASE_URL="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

# Remove trailing slash
BASE_URL="${BASE_URL%/}"

check() {
  local desc="$1"
  local expected_status="$2"
  shift 2
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$@")
  if [ "$status" = "$expected_status" ]; then
    echo "  PASS  $desc ($status)"
    ((PASS++))
  else
    echo "  FAIL  $desc (got $status, expected $expected_status)"
    ((FAIL++))
  fi
}

echo "Smoke testing $BASE_URL..."
echo ""

# --- Health endpoints ---
echo "Health:"
check "GET /health/live" "200" "$BASE_URL/health/live"
check "GET /health/ready" "200" "$BASE_URL/health/ready"
check "GET /health" "200" "$BASE_URL/health"
echo ""

# --- Auth-required endpoints (should 401 without token) ---
echo "Auth enforcement (expect 401):"
check "GET /api/v1/items (no auth)" "401" "$BASE_URL/api/v1/items"
check "GET /api/v1/users/me (no auth)" "401" "$BASE_URL/api/v1/users/me"
echo ""

# --- Billing (webhook endpoint accepts POST only) ---
echo "Method enforcement:"
check "GET /api/v1/billing/checkout (wrong method)" "405" "$BASE_URL/api/v1/billing/checkout"
echo ""

# --- Not-found ---
echo "404 handling:"
check "GET /nonexistent" "404" "$BASE_URL/nonexistent"
echo ""

# --- Summary ---
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
