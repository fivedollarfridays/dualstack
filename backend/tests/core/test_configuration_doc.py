"""Tests for central configuration reference document.

Validates that docs/CONFIGURATION.md exists and covers all env vars
from backend, frontend, and monitoring stacks.
"""

import re
from functools import cache
from pathlib import Path

PROJ_DIR = Path(__file__).resolve().parents[3]
CONFIG_DOC = PROJ_DIR / "docs" / "CONFIGURATION.md"


@cache
def _read() -> str:
    return CONFIG_DOC.read_text()


class TestConfigDocExists:
    def test_doc_exists(self) -> None:
        assert CONFIG_DOC.is_file()


class TestBackendVarsDocumented:
    """AC: All env vars from backend/.env.example documented."""

    def test_environment(self) -> None:
        assert "ENVIRONMENT" in _read()

    def test_database_url(self) -> None:
        assert "DATABASE_URL" in _read()

    def test_turso_database_url(self) -> None:
        assert "TURSO_DATABASE_URL" in _read()

    def test_turso_auth_token(self) -> None:
        assert "TURSO_AUTH_TOKEN" in _read()

    def test_clerk_jwks_url(self) -> None:
        assert "CLERK_JWKS_URL" in _read()

    def test_stripe_secret_key(self) -> None:
        assert "STRIPE_SECRET_KEY" in _read()

    def test_stripe_webhook_secret(self) -> None:
        assert "STRIPE_WEBHOOK_SECRET" in _read()

    def test_log_level(self) -> None:
        assert "LOG_LEVEL" in _read()

    def test_metrics_api_key(self) -> None:
        assert "METRICS_API_KEY" in _read()

    def test_cors_origins(self) -> None:
        assert "CORS_ORIGINS" in _read()


class TestFrontendVarsDocumented:
    """AC: All env vars from frontend/.env.example documented."""

    def test_clerk_publishable_key(self) -> None:
        assert "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" in _read()

    def test_api_url(self) -> None:
        assert "NEXT_PUBLIC_API_URL" in _read()

    def test_stripe_price_id(self) -> None:
        assert "NEXT_PUBLIC_STRIPE_PRO_PRICE_ID" in _read()

    def test_e2e_username(self) -> None:
        assert "E2E_CLERK_USER_USERNAME" in _read()

    def test_e2e_password(self) -> None:
        assert "E2E_CLERK_USER_PASSWORD" in _read()


class TestMonitoringVarsDocumented:
    """AC: All monitoring env vars documented."""

    def test_grafana_admin_password(self) -> None:
        assert "GRAFANA_ADMIN_PASSWORD" in _read()

    def test_prometheus_bearer_token(self) -> None:
        assert "PROMETHEUS_BEARER_TOKEN" in _read()

    def test_prometheus_basic_auth_password(self) -> None:
        assert "PROMETHEUS_BASIC_AUTH_PASSWORD" in _read()

    def test_gf_datasource_prom_user(self) -> None:
        assert "GF_DATASOURCE_PROM_USER" in _read()

    def test_gf_datasource_prom_password(self) -> None:
        assert "GF_DATASOURCE_PROM_PASSWORD" in _read()


class TestCrossStackDependencies:
    """AC: Cross-stack dependencies clearly noted."""

    def test_clerk_env_matching_noted(self) -> None:
        content = _read()
        assert re.search(
            r"CLERK_JWKS_URL.*NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY|NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.*CLERK_JWKS_URL",
            content,
            re.DOTALL,
        )

    def test_metrics_key_matching_noted(self) -> None:
        content = _read()
        assert re.search(
            r"METRICS_API_KEY.*PROMETHEUS_BEARER_TOKEN|PROMETHEUS_BEARER_TOKEN.*METRICS_API_KEY",
            content,
            re.DOTALL,
        )


class TestQuickStartTable:
    """AC: Quick-start table showing minimum variables for local development."""

    def test_has_quick_start_section(self) -> None:
        content = _read()
        assert re.search(
            r"#+.*quick.start|#+.*local.dev|#+.*minimum", content, re.IGNORECASE
        )
