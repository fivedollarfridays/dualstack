"""Health check models."""

from typing import Literal
from pydantic import BaseModel


class HealthStatus(BaseModel):
    """Overall health status."""

    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    uptime_seconds: float


class ServiceCheck(BaseModel):
    """Individual service health check."""

    name: str
    status: Literal["up", "down", "unknown"]
    latency_ms: float | None = None
    error: str | None = None


class ReadinessStatus(BaseModel):
    """Readiness probe response."""

    ready: bool
    checks: list[ServiceCheck]


class LivenessStatus(BaseModel):
    """Liveness probe response."""

    alive: bool
    uptime_seconds: float
