"""DualStack API - FastAPI + Next.js SaaS Starter Kit"""

import logging
from contextlib import asynccontextmanager

import stripe
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.core.metrics_routes import router as metrics_router
from app.core.middleware import LoggingMiddleware
from app.health import router as health_router

logger = logging.getLogger(__name__)

# Configure logging before app creation
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    settings = get_settings()
    if settings.environment != "development" and not settings.stripe_webhook_secret:
        raise RuntimeError(
            "STRIPE_WEBHOOK_SECRET must be set in non-development environments"
        )
    if settings.environment != "development" and not settings.clerk_jwks_url:
        raise RuntimeError(
            "CLERK_JWKS_URL must be set in non-development environments"
        )
    stripe.api_key = settings.stripe_secret_key
    yield


# Get settings for CORS configuration
settings = get_settings()

app = FastAPI(
    title="DualStack API",
    description="FastAPI + Next.js SaaS Starter Kit",
    version="1.0.0",
    lifespan=lifespan,
)

# Register exception handlers
register_exception_handlers(app)

# Add logging middleware (first, so it wraps everything)
app.add_middleware(LoggingMiddleware)

# CORS for frontend - configurable via CORS_ORIGINS env var
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include health router (no prefix for /health endpoints)
app.include_router(health_router)

# Include metrics router (no prefix for /metrics endpoint)
app.include_router(metrics_router)

# Include API routers (catch ImportError for optional modules)
try:
    from app.items.routes import router as items_router

    app.include_router(items_router, prefix="/api/v1")
except ImportError as e:
    logger.info("Items module not available: %s", e)

try:
    from app.billing.routes import router as billing_router
    from app.billing.routes import webhook_router

    app.include_router(billing_router, prefix="/api/v1")
    app.include_router(webhook_router)
except ImportError as e:
    logger.info("Billing module not available: %s", e)


@app.get("/")
async def root():
    return {"message": "DualStack API", "status": "running"}
