"""Stripe plan synchronization utility.

Syncs Stripe product/price catalog with the local database,
ensuring billing plans stay consistent across environments.
Handles creation, updates, and archival of plans.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class PlanRecord:
    """Local representation of a billing plan."""

    plan_id: str
    name: str
    description: str
    price_cents: int
    interval: str
    stripe_product_id: str = ""
    stripe_price_id: str = ""
    is_active: bool = True
    features: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialize plan to dictionary."""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "price_cents": self.price_cents,
            "interval": self.interval,
            "stripe_product_id": self.stripe_product_id,
            "stripe_price_id": self.stripe_price_id,
            "is_active": self.is_active,
            "features": list(self.features),
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ---------------------------------------------------------------------------
# Default plan catalog
# ---------------------------------------------------------------------------

# Customize these plans to match your billing page (frontend/src/app/(dashboard)/billing/page.tsx).
# The pricing here must stay in sync with what the frontend displays.
DEFAULT_PLANS: list[dict[str, Any]] = [
    {
        "plan_id": "free",
        "name": "Free",
        "description": "Get started with basic features at no cost.",
        "price_cents": 0,
        "interval": "month",
        "features": [
            "1 project",
            "Basic support",
            "Community access",
        ],
    },
    {
        "plan_id": "pro",
        "name": "Pro",
        "description": "For growing teams that need advanced features.",
        "price_cents": 1000,
        "interval": "month",
        "features": [
            "Unlimited projects",
            "Priority support",
            "API access",
            "Advanced analytics",
        ],
    },
]


# ---------------------------------------------------------------------------
# Synchronization logic
# ---------------------------------------------------------------------------


def load_local_plans(db_connection: Any) -> list[PlanRecord]:
    """Load all plans from the local database.

    Reads the plans table and returns PlanRecord instances
    for each active and inactive plan found.

    Args:
        db_connection: Database connection or session object.

    Returns:
        List of PlanRecord instances from the database.
    """
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT plan_id, name, description, price_cents, interval, "
        "stripe_product_id, stripe_price_id, is_active, features, "
        "metadata, created_at, updated_at FROM plans ORDER BY plan_id"
    )
    rows = cursor.fetchall()
    plans = []
    for row in rows:
        record = PlanRecord(
            plan_id=row[0],
            name=row[1],
            description=row[2],
            price_cents=row[3],
            interval=row[4],
            stripe_product_id=row[5] or "",
            stripe_price_id=row[6] or "",
            is_active=bool(row[7]),
            features=row[8] if isinstance(row[8], list) else [],
            metadata=row[9] if isinstance(row[9], dict) else {},
            created_at=row[10] or "",
            updated_at=row[11] or "",
        )
        plans.append(record)
    return plans


def fetch_stripe_products(stripe_client: Any) -> list[dict[str, Any]]:
    """Fetch all products and their prices from Stripe.

    Retrieves the complete product catalog from the Stripe API,
    including associated price objects for each product.

    Args:
        stripe_client: Initialized Stripe client instance.

    Returns:
        List of product dicts with nested price information.
    """
    products = []
    has_more = True
    starting_after = None

    while has_more:
        params: dict[str, Any] = {"limit": 100, "active": True}
        if starting_after:
            params["starting_after"] = starting_after
        response = stripe_client.products.list(**params)

        for product in response.data:
            prices = stripe_client.prices.list(product=product.id)
            products.append({
                "id": product.id,
                "name": product.name,
                "description": product.description or "",
                "metadata": dict(product.metadata),
                "prices": [{"id": p.id, "amount": p.unit_amount} for p in prices.data],
            })

        has_more = response.has_more
        if response.data:
            starting_after = response.data[-1].id

    return products


def _create_stripe_product(
    plan: PlanRecord,
    stripe_client: Any,
) -> None:
    """Create a new Stripe product and price for a plan."""
    product = stripe_client.products.create(
        name=plan.name,
        description=plan.description,
        metadata={"plan_id": plan.plan_id},
    )
    price = stripe_client.prices.create(
        product=product.id,
        unit_amount=plan.price_cents,
        currency="usd",
        recurring={"interval": plan.interval},
    )
    plan.stripe_product_id = product.id
    plan.stripe_price_id = price.id
    logger.info("Created Stripe product %s for plan %s", product.id, plan.plan_id)


def sync_plans_to_stripe(
    local_plans: list[PlanRecord],
    stripe_client: Any,
) -> dict[str, list[str]]:
    """Push local plan definitions to Stripe.

    Creates or updates Stripe products and prices to match
    the local plan catalog. Returns a summary of actions taken.

    Args:
        local_plans: List of PlanRecord to sync.
        stripe_client: Initialized Stripe client instance.

    Returns:
        Dict with 'created', 'updated', and 'skipped' plan ID lists.
    """
    result: dict[str, list[str]] = {"created": [], "updated": [], "skipped": []}
    remote = fetch_stripe_products(stripe_client)
    remote_by_name = {p["name"]: p for p in remote}

    for plan in local_plans:
        if not plan.is_active:
            result["skipped"].append(plan.plan_id)
            continue

        existing = remote_by_name.get(plan.name)
        if existing is None:
            _create_stripe_product(plan, stripe_client)
            result["created"].append(plan.plan_id)
        else:
            stripe_client.products.modify(
                existing["id"],
                name=plan.name,
                description=plan.description,
            )
            plan.stripe_product_id = existing["id"]
            result["updated"].append(plan.plan_id)

    return result


def save_sync_results(db_connection: Any, plans: list[PlanRecord]) -> int:
    """Persist updated Stripe IDs back to the local database.

    After syncing with Stripe, this writes the product and price
    IDs back to the local plans table so they stay in sync.

    Args:
        db_connection: Database connection or session object.
        plans: List of PlanRecord with updated Stripe IDs.

    Returns:
        Number of records updated in the database.
    """
    cursor = db_connection.cursor()
    count = 0
    now = datetime.now(timezone.utc).isoformat()

    for plan in plans:
        cursor.execute(
            "UPDATE plans SET stripe_product_id = ?, stripe_price_id = ?, "
            "updated_at = ? WHERE plan_id = ?",
            (plan.stripe_product_id, plan.stripe_price_id, now, plan.plan_id),
        )
        if cursor.rowcount > 0:
            count += 1

    db_connection.commit()
    logger.info("Saved sync results: %d records updated", count)
    return count


def validate_plan_catalog(plans: list[PlanRecord]) -> list[str]:
    """Validate the plan catalog for common issues.

    Checks for duplicate IDs, missing required fields, invalid
    pricing, and other data quality issues.

    Args:
        plans: List of PlanRecord to validate.

    Returns:
        List of validation error messages (empty if valid).
    """
    errors: list[str] = []
    seen_ids: set[str] = set()

    for plan in plans:
        if plan.plan_id in seen_ids:
            errors.append(f"Duplicate plan ID: {plan.plan_id}")
        seen_ids.add(plan.plan_id)

        if not plan.name:
            errors.append(f"Plan {plan.plan_id}: missing name")
        if plan.price_cents < 0:
            errors.append(f"Plan {plan.plan_id}: negative price")
        if plan.interval not in ("month", "year", "week"):
            errors.append(f"Plan {plan.plan_id}: invalid interval '{plan.interval}'")
        if plan.is_active and not plan.description:
            errors.append(f"Plan {plan.plan_id}: active plan missing description")

    return errors
