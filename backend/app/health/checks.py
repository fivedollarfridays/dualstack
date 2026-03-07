"""Health check endpoints."""

import logging
import time
from pathlib import Path
from fastapi import APIRouter, status, Response
from sqlalchemy import text

from app.core.database import get_engine
from app.health.models import (
    HealthStatus,
    ReadinessStatus,
    LivenessStatus,
    ServiceCheck,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

# Track app start time
APP_START_TIME = time.time()


def get_version() -> str:
    """Get application version from VERSION file."""
    version_file = Path(__file__).parent.parent.parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "1.0.0"


APP_VERSION = get_version()


async def check_database() -> ServiceCheck:
    """Check database connectivity."""
    start = time.time()
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        latency = (time.time() - start) * 1000
        return ServiceCheck(name="database", status="up", latency_ms=latency)
    except Exception:
        logger.exception("Database health check failed")
        return ServiceCheck(name="database", status="down", error="database unavailable")


@router.get("/live", response_model=LivenessStatus)
async def liveness():
    """
    Liveness probe - is the application running?

    Returns 200 if app is alive (can accept requests).
    Used by Kubernetes to restart unhealthy containers.
    """
    uptime = time.time() - APP_START_TIME
    return LivenessStatus(alive=True, uptime_seconds=uptime)


@router.get("/ready", response_model=ReadinessStatus)
async def readiness(response: Response):
    """
    Readiness probe - can the application serve traffic?

    Returns 200 if ready (DB connected, services available).
    Returns 503 if not ready.
    Used by Kubernetes to route traffic.
    """
    checks = []

    # Check database
    db_check = await check_database()
    checks.append(db_check)

    # Determine overall readiness
    ready = all(check.status == "up" for check in checks)

    # Return 503 if not ready
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessStatus(ready=ready, checks=checks)


@router.get("", response_model=HealthStatus)
@router.get("/", response_model=HealthStatus, include_in_schema=False)
async def health():
    """
    General health check with version and uptime info.

    Legacy endpoint - use /health/ready or /health/live for K8s.
    """
    uptime = time.time() - APP_START_TIME

    # Quick health determination
    try:
        db_check = await check_database()
        health_status = "healthy" if db_check.status == "up" else "degraded"
    except Exception:
        health_status = "unhealthy"

    return HealthStatus(
        status=health_status,
        version=APP_VERSION,
        uptime_seconds=uptime,
    )
