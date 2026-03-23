"""Tests for return type annotations on users/routes and health/checks (T25.5)."""

from typing import get_type_hints

from fastapi import Response


class TestUsersRouteReturnAnnotations:
    """Verify all functions in users/routes.py have return type annotations."""

    def test_get_current_user_has_return_type(self) -> None:
        from app.users.routes import get_current_user
        from app.users.schemas import SubscriptionInfoResponse

        hints = get_type_hints(get_current_user)
        assert "return" in hints, "get_current_user missing return annotation"
        assert hints["return"] is SubscriptionInfoResponse

    def test_get_user_profile_has_return_type(self) -> None:
        from app.users.routes import get_user_profile
        from app.users.schemas import UserProfileResponse

        hints = get_type_hints(get_user_profile)
        assert "return" in hints, "get_user_profile missing return annotation"
        assert hints["return"] is UserProfileResponse

    def test_update_user_profile_has_return_type(self) -> None:
        from app.users.routes import update_user_profile
        from app.users.schemas import UserProfileResponse

        hints = get_type_hints(update_user_profile)
        assert "return" in hints, "update_user_profile missing return annotation"
        assert hints["return"] is UserProfileResponse

    def test_delete_user_account_has_return_type(self) -> None:
        from app.users.routes import delete_user_account

        hints = get_type_hints(delete_user_account)
        assert "return" in hints, "delete_user_account missing return annotation"
        assert hints["return"] is Response


class TestHealthChecksReturnAnnotations:
    """Verify all functions in health/checks.py have return type annotations."""

    def test_check_database_has_return_type(self) -> None:
        from app.health.checks import check_database
        from app.health.models import ServiceCheck

        hints = get_type_hints(check_database)
        assert "return" in hints, "check_database missing return annotation"
        assert hints["return"] is ServiceCheck

    def test_liveness_has_return_type(self) -> None:
        from app.health.checks import liveness
        from app.health.models import LivenessStatus

        hints = get_type_hints(liveness)
        assert "return" in hints, "liveness missing return annotation"
        assert hints["return"] is LivenessStatus

    def test_readiness_has_return_type(self) -> None:
        from app.health.checks import readiness
        from app.health.models import ReadinessStatus

        hints = get_type_hints(readiness)
        assert "return" in hints, "readiness missing return annotation"
        assert hints["return"] is ReadinessStatus

    def test_health_has_return_type(self) -> None:
        from app.health.checks import health
        from app.health.models import HealthStatus

        hints = get_type_hints(health)
        assert "return" in hints, "health missing return annotation"
        assert hints["return"] is HealthStatus
