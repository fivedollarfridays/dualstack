"""
Metrics routes for Prometheus scraping.

Exposes /metrics endpoint that returns Prometheus metrics.
Protected by optional API key via X-Metrics-Key header.
"""

import hmac

from fastapi import APIRouter, Depends, Header, Request, Response
from prometheus_client import REGISTRY, generate_latest

from app.core.config import get_settings
from app.core.errors import AuthorizationError
from app.core.rate_limit import limiter


async def verify_metrics_key(x_metrics_key: str | None = Header(None)) -> None:
    """Verify the metrics API key if one is configured.

    When metrics_api_key is empty, the endpoint is open.
    When set, requests must provide a matching X-Metrics-Key header.
    Uses timing-safe comparison to prevent timing attacks.
    """
    settings = get_settings()
    if settings.metrics_api_key and not hmac.compare_digest(
        x_metrics_key or "", settings.metrics_api_key
    ):
        raise AuthorizationError(message="Invalid metrics API key")


router = APIRouter()


@router.get("/metrics", dependencies=[Depends(verify_metrics_key)])
@limiter.limit("60/minute")
async def metrics(request: Request) -> Response:
    """Expose Prometheus metrics.

    Returns:
        Response with Prometheus metrics in text format
    """
    metrics_data = generate_latest(REGISTRY)
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
