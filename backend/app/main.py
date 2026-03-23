"""DualStack API - FastAPI + Next.js SaaS Starter Kit"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import stripe
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.database import close_db
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.core.metrics_routes import router as metrics_router
from app.core.middleware import LoggingMiddleware
from app.core.rate_limit import limiter, rate_limit_handler
from app.core.security_headers import (
    ContentSizeLimitMiddleware,
    SecurityHeadersMiddleware,
)
from app.health import router as health_router

logger = logging.getLogger(__name__)

# Configure logging before app creation
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Manage application lifespan."""
    settings = get_settings()
    if settings.environment == "production" and not settings.stripe_webhook_secret:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET must be set in production")
    if settings.environment == "production" and not settings.clerk_jwks_url:
        raise RuntimeError("CLERK_JWKS_URL must be set in production")
    if (
        settings.environment == "production"
        and settings.clerk_jwks_url
        and not settings.clerk_audience
    ):
        raise RuntimeError(
            "CLERK_AUDIENCE must be set in production when CLERK_JWKS_URL is configured. "
            "This prevents cross-app JWT replay attacks."
        )
    if settings.clerk_jwks_url and not settings.clerk_audience:
        logger.warning(
            "WARNING: CLERK_AUDIENCE is not set. JWT audience validation is disabled. "
            "Set CLERK_AUDIENCE before deploying to production."
        )
    if not settings.clerk_jwks_url:
        logger.warning(
            "WARNING: Running without Clerk JWT validation. All X-User-ID headers "
            "are trusted. Do NOT deploy to production without setting CLERK_JWKS_URL."
        )
    if not settings.stripe_secret_key:
        logger.warning(
            "WARNING: STRIPE_SECRET_KEY is not set. Billing features will not work. "
            "Set this before deploying to production."
        )
    if not settings.storage_bucket:
        logger.warning(
            "WARNING: Object storage is not configured. File upload features will not work. "
            "Set STORAGE_BUCKET, STORAGE_ACCESS_KEY, and STORAGE_SECRET_KEY before deploying."
        )
    if (
        settings.environment == "production"
        and settings.forwarded_allow_ips == "127.0.0.1"
    ):
        raise RuntimeError(
            "FORWARDED_ALLOW_IPS must be set to your reverse proxy's IP range "
            "in production. The default '127.0.0.1' causes all clients to share "
            "a single rate-limit bucket behind a load balancer."
        )
    if settings.environment == "production" and not settings.metrics_api_key:
        raise RuntimeError(
            "METRICS_API_KEY is required in production to protect the /metrics endpoint."
        )
    stripe.api_key = settings.stripe_secret_key
    yield
    await close_db()


def _register_routers(application: FastAPI) -> None:
    """Register all routers on the application."""
    application.include_router(health_router)
    application.include_router(metrics_router)

    try:
        from app.items.routes import router as items_router

        application.include_router(items_router, prefix="/api/v1")
    except ImportError as e:
        logger.info("Items module not available: %s", e)

    try:
        from app.users.routes import router as users_router

        application.include_router(users_router, prefix="/api/v1")
    except ImportError as e:
        logger.info("Users module not available: %s", e)

    try:
        from app.billing.routes import router as billing_router
        from app.billing.routes import webhook_router

        application.include_router(billing_router, prefix="/api/v1")
        application.include_router(webhook_router)
    except ImportError as e:
        logger.info("Billing module not available: %s", e)

    try:
        from app.admin.routes import router as admin_router

        application.include_router(admin_router, prefix="/api/v1")
    except ImportError as e:
        logger.info("Admin module not available: %s", e)

    try:
        from app.files.routes import router as files_router

        application.include_router(files_router, prefix="/api/v1")
    except ImportError as e:
        logger.info("Files module not available: %s", e)

    try:
        from app.core.ws_routes import router as ws_router

        application.include_router(ws_router)
    except ImportError as e:
        logger.info("WebSocket module not available: %s", e)

    @application.get("/")
    @limiter.limit("120/minute")
    async def root(request: Request):
        return {"message": "DualStack API", "status": "running"}


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    is_production = settings.environment == "production"

    application = FastAPI(
        title="DualStack API",
        description="FastAPI + Next.js SaaS Starter Kit",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
        openapi_url=None if is_production else "/openapi.json",
    )

    register_exception_handlers(application)
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, rate_limit_handler)

    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(ContentSizeLimitMiddleware)
    application.add_middleware(LoggingMiddleware)
    cors_headers = ["Authorization", "Content-Type"]
    if not is_production:
        cors_headers.append("X-User-ID")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=bool(settings.clerk_jwks_url),
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=cors_headers,
    )

    _register_routers(application)
    return application


app = create_app()
