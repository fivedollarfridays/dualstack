"""Tests for billing plan definitions."""

from app.billing.plans import (
    ACTIVE_STATUSES,
    PLAN_TIERS,
    get_plan_features,
    get_plan_limit,
)


class TestPlanTiers:
    def test_free_tier_exists(self):
        assert "free" in PLAN_TIERS

    def test_pro_tier_exists(self):
        assert "pro" in PLAN_TIERS

    def test_enterprise_tier_exists(self):
        assert "enterprise" in PLAN_TIERS

    def test_each_tier_has_features_and_limits(self):
        for name, tier in PLAN_TIERS.items():
            assert "features" in tier, f"{name} missing features"
            assert "limits" in tier, f"{name} missing limits"


class TestGetPlanFeatures:
    def test_free_has_basic_features(self):
        features = get_plan_features("free")
        assert "items.read" in features
        assert "items.create" in features

    def test_pro_has_portal_feature(self):
        features = get_plan_features("pro")
        assert "billing.portal" in features

    def test_enterprise_wildcard_grants_all(self):
        features = get_plan_features("enterprise")
        assert "*" in features

    def test_unknown_plan_defaults_to_free(self):
        features = get_plan_features("nonexistent_plan")
        free_features = get_plan_features("free")
        assert features == free_features


class TestGetPlanLimit:
    def test_free_has_max_items_limit(self):
        limit = get_plan_limit("free", "max_items")
        assert isinstance(limit, int)
        assert limit > 0
        assert limit <= 25  # reasonable free tier limit

    def test_pro_has_higher_limit(self):
        free_limit = get_plan_limit("free", "max_items")
        pro_limit = get_plan_limit("pro", "max_items")
        assert pro_limit > free_limit

    def test_enterprise_unlimited(self):
        limit = get_plan_limit("enterprise", "max_items")
        assert limit == -1

    def test_unknown_limit_returns_zero(self):
        limit = get_plan_limit("free", "nonexistent_limit")
        assert limit == 0

    def test_unknown_plan_uses_free_limits(self):
        limit = get_plan_limit("unknown", "max_items")
        free_limit = get_plan_limit("free", "max_items")
        assert limit == free_limit


class TestActiveStatuses:
    def test_active_is_active(self):
        assert "active" in ACTIVE_STATUSES

    def test_trialing_is_active(self):
        assert "trialing" in ACTIVE_STATUSES

    def test_canceled_is_not_active(self):
        assert "canceled" not in ACTIVE_STATUSES

    def test_past_due_is_not_active(self):
        assert "past_due" not in ACTIVE_STATUSES
