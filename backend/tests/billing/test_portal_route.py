"""Tests for billing portal route."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.routes import router
from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.core.exception_handlers import register_exception_handlers
from app.users.service import get_or_create_user, link_stripe_customer
from fastapi import FastAPI
from tests.helpers import mock_settings_with_cors


def _create_test_app(db_session: AsyncSession) -> FastAPI:
    """Create a test app with db override."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router, prefix="/api/v1")

    async def _override_auth() -> str:
        return "clerk_portal_user"

    async def _override_db():
        yield db_session

    app.dependency_overrides[get_current_user_id] = _override_auth
    app.dependency_overrides[get_db] = _override_db
    return app


def _create_unauthed_app(db_session: AsyncSession) -> FastAPI:
    """Create a test app without auth override (401 tests)."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router, prefix="/api/v1")

    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    return app


class TestPortalRoute:
    @pytest.mark.asyncio
    @patch("app.core.url_validation.get_settings")
    async def test_returns_portal_url_for_subscribed_user(
        self, mock_gs: MagicMock, db_session: AsyncSession
    ):
        """Authenticated user with stripe_customer_id gets portal URL."""
        mock_gs.return_value = mock_settings_with_cors("https://example.com")
        await get_or_create_user(db_session, "clerk_portal_user")
        await link_stripe_customer(db_session, "clerk_portal_user", "cus_portal_123")

        app = _create_test_app(db_session)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch(
                "app.billing.service.create_portal_session",
                new_callable=AsyncMock,
                return_value="https://billing.stripe.com/portal_abc",
            ):
                response = await client.post(
                    "/api/v1/billing/portal",
                    json={"return_url": "https://example.com/dashboard"},
                )

        assert response.status_code == 200
        assert response.json() == {"url": "https://billing.stripe.com/portal_abc"}

    @pytest.mark.asyncio
    @patch("app.core.url_validation.get_settings")
    async def test_returns_404_when_no_stripe_customer(
        self, mock_gs: MagicMock, db_session: AsyncSession
    ):
        """User exists but has no stripe_customer_id."""
        mock_gs.return_value = mock_settings_with_cors("https://example.com")
        await get_or_create_user(db_session, "clerk_portal_user")

        app = _create_test_app(db_session)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/billing/portal",
                json={"return_url": "https://example.com/dashboard"},
            )

        assert response.status_code == 404
        body = response.json()
        assert body["error"]["code"] == "NOT_FOUND"
        assert "subscribe" in body["error"]["message"].lower()

    @pytest.mark.asyncio
    @patch("app.core.url_validation.get_settings")
    async def test_returns_404_when_user_not_found(
        self, mock_gs: MagicMock, db_session: AsyncSession
    ):
        """User not in database at all."""
        mock_gs.return_value = mock_settings_with_cors("https://example.com")

        app = _create_test_app(db_session)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/billing/portal",
                json={"return_url": "https://example.com/dashboard"},
            )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    @patch("app.core.url_validation.get_settings")
    async def test_audit_event_on_success(
        self, mock_gs: MagicMock, db_session: AsyncSession
    ):
        """Successful portal creation logs audit event."""
        mock_gs.return_value = mock_settings_with_cors("https://example.com")
        await get_or_create_user(db_session, "clerk_portal_user")
        await link_stripe_customer(db_session, "clerk_portal_user", "cus_audit_portal")

        app = _create_test_app(db_session)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with (
                patch(
                    "app.billing.service.create_portal_session",
                    new_callable=AsyncMock,
                    return_value="https://billing.stripe.com/portal_abc",
                ),
                patch(
                    "app.billing.routes.persist_audit_event", new_callable=AsyncMock
                ) as mock_audit,
            ):
                response = await client.post(
                    "/api/v1/billing/portal",
                    json={"return_url": "https://example.com/dashboard"},
                )

        assert response.status_code == 200
        mock_audit.assert_called()
        kwargs = mock_audit.call_args[1]
        assert kwargs["action"] == "billing.portal_created"
