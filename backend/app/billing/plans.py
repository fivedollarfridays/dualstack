"""Subscription plan tiers and feature definitions."""

from typing import TypedDict

DEFAULT_PLAN: str = "free"
DEFAULT_STATUS: str = "none"

ACTIVE_STATUSES: frozenset[str] = frozenset({"active", "trialing"})


class PlanTier(TypedDict):
    features: set[str]
    limits: dict[str, int]


PLAN_TIERS: dict[str, PlanTier] = {
    "free": {
        "features": {"items.create", "items.read", "items.update", "items.delete"},
        "limits": {"max_items": 10},
    },
    "pro": {
        "features": {
            "items.create",
            "items.read",
            "items.update",
            "items.delete",
            "billing.portal",
            "export.csv",
        },
        "limits": {"max_items": 1000},
    },
    "enterprise": {
        "features": {"*"},
        "limits": {"max_items": -1},
    },
}


def get_plan_features(plan_name: str) -> set[str]:
    """Return the feature set for a plan. Unknown plans default to free."""
    tier = PLAN_TIERS.get(plan_name, PLAN_TIERS["free"])
    return tier["features"]


def get_plan_limit(plan_name: str, limit_key: str) -> int:
    """Return a numeric limit for a plan. Unknown limits return 0."""
    tier = PLAN_TIERS.get(plan_name, PLAN_TIERS["free"])
    return tier["limits"].get(limit_key, 0)
