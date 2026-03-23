"""Health check endpoints."""

import logging

from fastapi import APIRouter, Request, status, Response
from sqlalchemy import text

from app.core.database import get_engine
from app.core.rate_limit import limiter
from app.health.models import (
    HealthStatus,
    ReadinessStatus,
    LivenessStatus,
    ServiceCheck,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


async def check_database() -> ServiceCheck:
    """Check database connectivity."""
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return ServiceCheck(name="database", status="up")
    except Exception:
        logger.exception("Database health check failed")
        return ServiceCheck(
            name="database", status="down", error="database unavailable"
        )


@router.get("/live", response_model=LivenessStatus)
@limiter.limit("120/minute")
async def liveness(request: Request) -> LivenessStatus:
    """
    Liveness probe - is the application running?

    Returns 200 if app is alive (can accept requests).
    Used by Kubernetes to restart unhealthy containers.
    """
    return LivenessStatus(alive=True)


@router.get("/ready", response_model=ReadinessStatus)
@limiter.limit("120/minute")
async def readiness(request: Request, response: Response) -> ReadinessStatus:
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
@limiter.limit("120/minute")
async def health(request: Request) -> HealthStatus:
    """
    General health check - status only.

    Use /health/ready or /health/live for K8s probes.
    """
    try:
        db_check = await check_database()
        health_status = "healthy" if db_check.status == "up" else "degraded"
    except Exception:
        health_status = "unhealthy"

    return HealthStatus(status=health_status)
