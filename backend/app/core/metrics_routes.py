"""
Metrics routes for Prometheus scraping.

Exposes /metrics endpoint that returns Prometheus metrics.
"""

from fastapi import APIRouter, Response
from prometheus_client import REGISTRY, generate_latest

router = APIRouter()


@router.get("/metrics")
async def metrics() -> Response:
    """Expose Prometheus metrics.

    Returns:
        Response with Prometheus metrics in text format
    """
    metrics_data = generate_latest(REGISTRY)
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
