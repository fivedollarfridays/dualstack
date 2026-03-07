#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
# --forwarded-allow-ips='*': Trusts X-Forwarded-For from any source. Safe behind
# Render's load balancer which overwrites the header with the real client IP.
# Direct-to-container access must be blocked at the network level.
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'
