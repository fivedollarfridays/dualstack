#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
# FORWARDED_ALLOW_IPS: Controls which proxies are trusted for X-Forwarded-For.
# Set to your load balancer IPs in production (e.g., Render's IP ranges).
# Defaults to 127.0.0.1 for safety — set to '*' only behind a trusted reverse proxy
# that overwrites X-Forwarded-For (e.g., Render, AWS ALB).
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="${FORWARDED_ALLOW_IPS:-127.0.0.1}"
