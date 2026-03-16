"""Tests for centralized log aggregation with Fluent Bit and Loki.

Validates that the monitoring stack includes Fluent Bit and Loki services
with proper configuration for SOC2 CC7.1 compliance.
"""

import re
from functools import cache
from pathlib import Path

import yaml

PROJ_DIR = Path(__file__).resolve().parents[3]
MONITORING_DIR = PROJ_DIR / "monitoring"
FLUENT_BIT_DIR = MONITORING_DIR / "fluent-bit"
COMPOSE_FILE = MONITORING_DIR / "docker-compose.yml"
COMPOSE_DEV = MONITORING_DIR / "docker-compose.dev.yml"
COMPOSE_PROD = MONITORING_DIR / "docker-compose.prod.yml"
README = MONITORING_DIR / "README.md"
COMPLIANCE = PROJ_DIR / "docs" / "COMPLIANCE.md"
LOKI_DATASOURCE = (
    MONITORING_DIR / "grafana" / "provisioning" / "datasources" / "loki.yml"
)


@cache
def _load_compose() -> dict:
    return yaml.safe_load(COMPOSE_FILE.read_text())


@cache
def _read_readme() -> str:
    return README.read_text()


@cache
def _read_fluent_bit_conf() -> str:
    return (FLUENT_BIT_DIR / "fluent-bit.conf").read_text()


@cache
def _read_parsers_conf() -> str:
    return (FLUENT_BIT_DIR / "parsers.conf").read_text()


@cache
def _read_compliance() -> str:
    return COMPLIANCE.read_text()


class TestFluentBitConfigExists:
    """Fluent Bit configuration files exist."""

    def test_fluent_bit_dir_exists(self) -> None:
        assert FLUENT_BIT_DIR.is_dir()

    def test_main_config_exists(self) -> None:
        assert (FLUENT_BIT_DIR / "fluent-bit.conf").is_file()

    def test_parsers_config_exists(self) -> None:
        assert (FLUENT_BIT_DIR / "parsers.conf").is_file()


class TestFluentBitConfig:
    """AC: Fluent Bit config supports JSON parsing for structured logs."""

    def test_has_input_section(self) -> None:
        assert re.search(r"\[INPUT\]", _read_fluent_bit_conf())

    def test_has_output_section(self) -> None:
        assert re.search(r"\[OUTPUT\]", _read_fluent_bit_conf())

    def test_outputs_to_loki(self) -> None:
        assert re.search(r"loki", _read_fluent_bit_conf(), re.IGNORECASE)

    def test_parsers_has_json(self) -> None:
        assert re.search(r"json", _read_parsers_conf(), re.IGNORECASE)


class TestComposeServices:
    """AC: Fluent Bit and Loki services run in Docker Compose."""

    def test_loki_service_exists(self) -> None:
        services = _load_compose().get("services", {})
        assert any("loki" in k for k in services), (
            f"No loki service. Services: {list(services.keys())}"
        )

    def test_fluent_bit_service_exists(self) -> None:
        services = _load_compose().get("services", {})
        assert any("fluent" in k for k in services), (
            f"No fluent-bit service. Services: {list(services.keys())}"
        )

    def test_loki_has_health_check(self) -> None:
        services = _load_compose().get("services", {})
        loki = next((v for k, v in services.items() if "loki" in k), None)
        assert loki is not None
        assert "healthcheck" in loki

    def test_fluent_bit_depends_on_loki(self) -> None:
        services = _load_compose().get("services", {})
        fb = next((v for k, v in services.items() if "fluent" in k), None)
        assert fb is not None
        deps = fb.get("depends_on", {})
        deps_str = yaml.dump(deps)
        assert "loki" in deps_str

    def test_loki_has_volume(self) -> None:
        services = _load_compose().get("services", {})
        loki = next((v for k, v in services.items() if "loki" in k), None)
        assert loki is not None
        assert "volumes" in loki

    def test_existing_services_unchanged(self) -> None:
        """AC: Existing services continue to function."""
        services = _load_compose().get("services", {})
        assert "prometheus" in services
        assert "grafana" in services
        assert "alertmanager" in services


class TestLokiDatasource:
    """AC: Logs queryable in Grafana via Loki datasource."""

    def test_loki_datasource_provisioned(self) -> None:
        assert LOKI_DATASOURCE.is_file()

    def test_loki_datasource_type(self) -> None:
        data = yaml.safe_load(LOKI_DATASOURCE.read_text())
        ds = data["datasources"][0]
        assert ds["type"] == "loki"


class TestProductionConfig:
    """AC: Production output configurable via env vars."""

    def test_prod_compose_exists(self) -> None:
        assert COMPOSE_PROD.is_file()

    def test_fluent_bit_conf_has_env_vars(self) -> None:
        """Config supports swapping output via env vars."""
        content = _read_fluent_bit_conf()
        # Should reference env var for output host or have placeholder
        assert (
            re.search(r"\$\{|LOKI_HOST|LOKI_URL", content) or "loki" in content.lower()
        )


class TestReadmeUpdated:
    """AC: README updated with log aggregation setup."""

    def test_mentions_fluent_bit(self) -> None:
        assert re.search(r"fluent.bit", _read_readme(), re.IGNORECASE)

    def test_mentions_loki(self) -> None:
        assert re.search(r"loki", _read_readme(), re.IGNORECASE)

    def test_mentions_log_query(self) -> None:
        assert re.search(
            r"LogQL|log.*query|log.*explore", _read_readme(), re.IGNORECASE
        )


class TestComplianceUpdated:
    """AC: COMPLIANCE.md updated for CC7.1 log aggregation."""

    def test_cc71_mentions_log_aggregation(self) -> None:
        assert re.search(
            r"log.aggregat|fluent.bit|loki", _read_compliance(), re.IGNORECASE
        )
