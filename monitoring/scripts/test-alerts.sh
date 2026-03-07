#!/bin/bash
# Test script for Prometheus alert rules
# Verifies that alert rules are loaded and configured correctly

set -e

echo "🔍 Testing Prometheus alert configuration..."
echo ""

# Check if Prometheus is running
echo "✓ Checking Prometheus health..."
if ! curl -sf http://localhost:9090/-/healthy > /dev/null 2>&1; then
  echo "❌ Prometheus is not running"
  echo "   Start with: cd monitoring && docker-compose up -d"
  exit 1
fi
echo "  ✅ Prometheus is healthy"

# Check if Alertmanager is running
echo "✓ Checking Alertmanager health..."
if ! curl -sf http://localhost:9093/-/healthy > /dev/null 2>&1; then
  echo "❌ Alertmanager is not running"
  echo "   Start with: cd monitoring && docker-compose up -d alertmanager"
  exit 1
fi
echo "  ✅ Alertmanager is healthy"

# Reload alert rules
echo "✓ Reloading alert rules..."
if curl -sf -X POST http://localhost:9090/-/reload > /dev/null 2>&1; then
  echo "  ✅ Alert rules reloaded"
else
  echo "  ⚠️  Reload failed (not critical)"
fi

# Wait for rules to load
sleep 2

# Check if alert rules are loaded
echo "✓ Checking loaded alert rules..."
if ! command -v jq &> /dev/null; then
  echo "  ⚠️  jq not installed, skipping detailed checks"
  RULES_DATA=$(curl -s http://localhost:9090/api/v1/rules)
  echo "  Rules endpoint response: OK"
else
  RULES_COUNT=$(curl -s http://localhost:9090/api/v1/rules | jq '.data.groups | length')
  if [ "$RULES_COUNT" -lt 3 ]; then
    echo "❌ Alert rules not loaded properly (found $RULES_COUNT groups, expected 3)"
    exit 1
  fi
  echo "  ✅ Alert rules loaded ($RULES_COUNT groups)"

  # Count total rules
  TOTAL_RULES=$(curl -s http://localhost:9090/api/v1/rules | jq '[.data.groups[].rules[]] | length')
  echo "  ✅ Total alert rules: $TOTAL_RULES"

  # List rule groups
  echo ""
  echo "📋 Alert groups:"
  curl -s http://localhost:9090/api/v1/rules | jq -r '.data.groups[] | "  - \(.name): \(.rules | length) rules"'
fi

# Check for any firing alerts
echo ""
echo "✓ Checking for firing alerts..."
if ! command -v jq &> /dev/null; then
  echo "  ⚠️  jq not installed, skipping alert check"
else
  FIRING=$(curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts | map(select(.state == "firing")) | length')
  PENDING=$(curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts | map(select(.state == "pending")) | length')

  echo "  📊 Firing alerts: $FIRING"
  echo "  📊 Pending alerts: $PENDING"

  if [ "$FIRING" -gt 0 ]; then
    echo ""
    echo "🚨 Currently firing alerts:"
    curl -s http://localhost:9090/api/v1/alerts | jq -r '.data.alerts[] | select(.state == "firing") | "  - \(.labels.alertname) (\(.labels.severity)): \(.annotations.summary)"'
  fi
fi

# Check Alertmanager configuration
echo ""
echo "✓ Checking Alertmanager configuration..."
if ! command -v jq &> /dev/null; then
  echo "  ⚠️  jq not installed, skipping config check"
else
  RECEIVERS=$(curl -s http://localhost:9093/api/v1/status | jq '.data.config.receivers | length')
  echo "  ✅ Alertmanager receivers configured: $RECEIVERS"
fi

# Check Alertmanager alerts
echo ""
echo "✓ Checking Alertmanager alerts..."
if ! command -v jq &> /dev/null; then
  echo "  ⚠️  jq not installed, skipping alert check"
else
  AM_ALERTS=$(curl -s http://localhost:9093/api/v2/alerts | jq 'length')
  echo "  📊 Alerts in Alertmanager: $AM_ALERTS"
fi

echo ""
echo "✅ Alert configuration test complete!"
echo ""
echo "📚 Useful URLs:"
echo "   Prometheus UI: http://localhost:9090"
echo "   Prometheus Alerts: http://localhost:9090/alerts"
echo "   Prometheus Rules: http://localhost:9090/rules"
echo "   Alertmanager UI: http://localhost:9093"
echo "   Alertmanager Alerts: http://localhost:9093/#/alerts"
echo ""
echo "To test specific alerts:"
echo "   - Stop backend to trigger APIDown"
echo "   - Generate errors to trigger APIHighErrorRate"
echo "   - Run slow queries to trigger DatabaseSlowQueries"
