"""Tests for feature gating entitlements."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI

from fastapi import Depends

from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.core.entitlements import require_feature
from app.core.exception_handlers import register_exception_handlers
from app.users.service import get_or_create_user, update_user
from app.users.schemas import UserUpdate


class TestRequireFeature:
    """Test require_feature dependency."""

    @pytest.mark.asyncio
    async def test_allows_access_for_entitled_user(self, db_session: AsyncSession):
        """Active pro user can access billing.portal feature."""
        from app.core.entitlements import check_feature_access

        await get_or_create_user(db_session, "clerk_pro")
        await update_user(
            db_session,
            "clerk_pro",
            UserUpdate(subscription_plan="pro", subscription_status="active"),
        )

        result = await check_feature_access(db_session, "clerk_pro", "billing.portal")
        assert result is True

    @pytest.mark.asyncio
    async def test_denies_access_for_missing_feature(self, db_session: AsyncSession):
        """Free user cannot access billing.portal feature."""
        from app.core.entitlements import check_feature_access

        await get_or_create_user(db_session, "clerk_free")

        result = await check_feature_access(db_session, "clerk_free", "billing.portal")
        assert result is False

    @pytest.mark.asyncio
    async def test_denies_access_for_canceled_subscription(
        self, db_session: AsyncSession
    ):
        """Canceled pro user cannot access pro features."""
        from app.core.entitlements import check_feature_access

        await get_or_create_user(db_session, "clerk_canceled")
        await update_user(
            db_session,
            "clerk_canceled",
            UserUpdate(subscription_plan="pro", subscription_status="canceled"),
        )

        result = await check_feature_access(
            db_session, "clerk_canceled", "billing.portal"
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_allows_free_features_for_canceled_user(
        self, db_session: AsyncSession
    ):
        """Canceled user still gets free-tier features."""
        from app.core.entitlements import check_feature_access

        await get_or_create_user(db_session, "clerk_can_free")
        await update_user(
            db_session,
            "clerk_can_free",
            UserUpdate(subscription_plan="pro", subscription_status="canceled"),
        )

        result = await check_feature_access(db_session, "clerk_can_free", "items.read")
        assert result is True

    @pytest.mark.asyncio
    async def test_enterprise_wildcard_grants_any_feature(
        self, db_session: AsyncSession
    ):
        """Enterprise user with wildcard has access to everything."""
        from app.core.entitlements import check_feature_access

        await get_or_create_user(db_session, "clerk_ent")
        await update_user(
            db_session,
            "clerk_ent",
            UserUpdate(subscription_plan="enterprise", subscription_status="active"),
        )

        result = await check_feature_access(
            db_session, "clerk_ent", "some.random.feature"
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_unknown_user_defaults_to_free(self, db_session: AsyncSession):
        """User not in database gets free plan features."""
        from app.core.entitlements import check_feature_access

        result = await check_feature_access(db_session, "clerk_ghost", "items.read")
        assert result is True

    @pytest.mark.asyncio
    async def test_unknown_user_denied_pro_features(self, db_session: AsyncSession):
        """User not in database cannot access pro features."""
        from app.core.entitlements import check_feature_access

        result = await check_feature_access(db_session, "clerk_ghost", "billing.portal")
        assert result is False


class TestRequireFeatureErrorEnvelope:
    """Test that require_feature returns standard error envelope on denial."""

    @pytest.mark.asyncio
    async def test_returns_403_with_error_envelope(self, db_session: AsyncSession):
        """Denied feature access returns {"error": {"code", "message"}} envelope."""
        await get_or_create_user(db_session, "clerk_free_envelope")

        app = FastAPI()
        register_exception_handlers(app)

        @app.get(
            "/test-gated", dependencies=[Depends(require_feature("billing.portal"))]
        )
        async def gated_route():
            return {"ok": True}

        async def _override_auth() -> str:
            return "clerk_free_envelope"

        async def _override_db():
            yield db_session

        app.dependency_overrides[get_current_user_id] = _override_auth
        app.dependency_overrides[get_db] = _override_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test-gated")

        assert response.status_code == 403
        body = response.json()
        assert body["error"]["code"] == "AUTHORIZATION_ERROR"
        assert "requires" in body["error"]["message"].lower()


class TestGetUserEntitlements:
    """Test get_user_entitlements helper."""

    @pytest.mark.asyncio
    async def test_returns_plan_and_features(self, db_session: AsyncSession):
        """Returns dict with plan, status, features, limits."""
        from app.core.entitlements import get_user_entitlements

        await get_or_create_user(db_session, "clerk_ent_check")
        await update_user(
            db_session,
            "clerk_ent_check",
            UserUpdate(subscription_plan="pro", subscription_status="active"),
        )

        ent = await get_user_entitlements(db_session, "clerk_ent_check")
        assert ent["plan"] == "pro"
        assert ent["status"] == "active"
        assert "billing.portal" in ent["features"]
        assert "max_items" in ent["limits"]

    @pytest.mark.asyncio
    async def test_unknown_user_returns_free(self, db_session: AsyncSession):
        """Unknown user gets free plan entitlements."""
        from app.core.entitlements import get_user_entitlements

        ent = await get_user_entitlements(db_session, "clerk_nobody")
        assert ent["plan"] == "free"
        assert ent["status"] == "none"
