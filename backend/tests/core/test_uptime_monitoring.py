"""Tests for external uptime monitoring with PagerDuty integration.

Validates that the monitoring stack includes uptime alert rules,
PagerDuty receiver configuration, monitoring documentation, and
a health check script for SOC2 CC7.1 compliance.
"""

import re
from functools import cache
from pathlib import Path

import yaml

PROJ_DIR = Path(__file__).resolve().parents[3]
MONITORING_DIR = PROJ_DIR / "monitoring"
ALERTS_DIR = MONITORING_DIR / "prometheus" / "alerts"
ALERTMANAGER_YML = MONITORING_DIR / "alertmanager" / "alertmanager.yml"
MONITORING_DOC = PROJ_DIR / "docs" / "MONITORING.md"
COMPLIANCE_DOC = PROJ_DIR / "docs" / "COMPLIANCE.md"
HEALTHCHECK_SCRIPT = PROJ_DIR / "scripts" / "healthcheck.sh"


@cache
def _load_uptime_rules() -> dict:
    return yaml.safe_load((ALERTS_DIR / "uptime.yml").read_text())


@cache
def _load_alertmanager() -> dict:
    return yaml.safe_load(ALERTMANAGER_YML.read_text())


@cache
def _read_monitoring_doc() -> str:
    return MONITORING_DOC.read_text()


@cache
def _read_compliance() -> str:
    return COMPLIANCE_DOC.read_text()


@cache
def _read_healthcheck() -> str:
    return HEALTHCHECK_SCRIPT.read_text()


class TestUptimeAlertRules:
    """AC: Prometheus alert rules exist for health endpoint failures."""

    def test_uptime_rules_file_exists(self) -> None:
        assert (ALERTS_DIR / "uptime.yml").is_file()

    def test_has_health_live_down_alert(self) -> None:
        rules = _load_uptime_rules()
        names = [r["alert"] for g in rules["groups"] for r in g["rules"]]
        assert "HealthLiveEndpointDown" in names

    def test_has_health_ready_down_alert(self) -> None:
        rules = _load_uptime_rules()
        names = [r["alert"] for g in rules["groups"] for r in g["rules"]]
        assert "HealthReadyEndpointDown" in names

    def test_has_health_endpoint_slow_alert(self) -> None:
        rules = _load_uptime_rules()
        names = [r["alert"] for g in rules["groups"] for r in g["rules"]]
        assert "HealthEndpointSlow" in names

    def test_live_down_is_critical(self) -> None:
        rules = _load_uptime_rules()
        rule = next(
            (
                r
                for g in rules["groups"]
                for r in g["rules"]
                if r["alert"] == "HealthLiveEndpointDown"
            ),
            None,
        )
        assert rule is not None, "HealthLiveEndpointDown rule not found"
        assert rule["labels"]["severity"] == "critical"

    def test_slow_is_warning(self) -> None:
        rules = _load_uptime_rules()
        rule = next(
            (
                r
                for g in rules["groups"]
                for r in g["rules"]
                if r["alert"] == "HealthEndpointSlow"
            ),
            None,
        )
        assert rule is not None, "HealthEndpointSlow rule not found"
        assert rule["labels"]["severity"] == "warning"


class TestAlertmanagerPagerDuty:
    """AC: Alertmanager config includes PagerDuty receiver."""

    def test_has_pagerduty_receiver(self) -> None:
        config = _load_alertmanager()
        receivers = config.get("receivers", [])
        receiver_text = yaml.dump(receivers)
        assert "pagerduty" in receiver_text.lower()

    def test_pagerduty_uses_env_var(self) -> None:
        """PagerDuty integration key is templated, not hardcoded."""
        content = yaml.dump(_load_alertmanager())
        assert re.search(r"PAGERDUTY", content)

    def test_critical_routes_to_critical_receiver(self) -> None:
        """Critical health alerts route to the critical receiver."""
        config = _load_alertmanager()
        routes = config["route"].get("routes", [])
        critical_route = next(
            (r for r in routes if r.get("match", {}).get("severity") == "critical"),
            None,
        )
        assert critical_route is not None

    def test_inhibit_ready_when_live_down(self) -> None:
        """Suppress HealthReadyEndpointDown when HealthLiveEndpointDown is firing."""
        config = _load_alertmanager()
        inhibit_rules = config.get("inhibit_rules", [])
        inhibit_text = yaml.dump(inhibit_rules)
        assert "HealthLiveEndpointDown" in inhibit_text


class TestMonitoringDoc:
    """AC: docs/MONITORING.md includes setup guides."""

    def test_monitoring_doc_exists(self) -> None:
        assert MONITORING_DOC.is_file()

    def test_mentions_uptime_monitoring(self) -> None:
        content = _read_monitoring_doc()
        assert re.search(r"uptime.monitor", content, re.IGNORECASE)

    def test_mentions_managed_service(self) -> None:
        """At least one managed uptime service mentioned."""
        content = _read_monitoring_doc()
        assert re.search(
            r"UptimeRobot|Pingdom|Better.Uptime|BetterStack",
            content,
            re.IGNORECASE,
        )

    def test_mentions_pagerduty_setup(self) -> None:
        content = _read_monitoring_doc()
        assert re.search(r"PagerDuty", content)

    def test_mentions_health_endpoints(self) -> None:
        content = _read_monitoring_doc()
        assert "/health/live" in content
        assert "/health/ready" in content

    def test_mentions_alert_severity_mapping(self) -> None:
        content = _read_monitoring_doc()
        assert re.search(r"critical|warning|info", content, re.IGNORECASE)


class TestHealthcheckScript:
    """AC: scripts/healthcheck.sh checks both health endpoints."""

    def test_script_exists(self) -> None:
        assert HEALTHCHECK_SCRIPT.is_file()

    def test_script_is_executable(self) -> None:
        import os

        assert os.access(HEALTHCHECK_SCRIPT, os.X_OK)

    def test_checks_live_endpoint(self) -> None:
        content = _read_healthcheck()
        assert "/health/live" in content

    def test_checks_ready_endpoint(self) -> None:
        content = _read_healthcheck()
        assert "/health/ready" in content

    def test_supports_url_flag(self) -> None:
        content = _read_healthcheck()
        assert "--url" in content

    def test_exits_nonzero_on_failure(self) -> None:
        """Script uses exit 1 or set -e for failure handling."""
        content = _read_healthcheck()
        assert re.search(r"exit\s+[1-9]|set\s+-e", content)


class TestExistingAlertsUnchanged:
    """AC: Existing alert rules continue to function."""

    def test_critical_rules_exist(self) -> None:
        data = yaml.safe_load((ALERTS_DIR / "critical.yml").read_text())
        names = [r["alert"] for g in data["groups"] for r in g["rules"]]
        assert "APIHighErrorRate" in names
        assert "APIDown" in names
        assert "DatabasePoolExhausted" in names

    def test_warnings_rules_exist(self) -> None:
        data = yaml.safe_load((ALERTS_DIR / "warnings.yml").read_text())
        names = [r["alert"] for g in data["groups"] for r in g["rules"]]
        assert "APIHighLatency" in names

    def test_info_rules_exist(self) -> None:
        data = yaml.safe_load((ALERTS_DIR / "info.yml").read_text())
        names = [r["alert"] for g in data["groups"] for r in g["rules"]]
        assert "DatabasePoolHighUtilization" in names


class TestComplianceUpdated:
    """AC: COMPLIANCE.md updated to mark CC7.1 uptime gap as addressed."""

    def test_cc71_uptime_addressed(self) -> None:
        content = _read_compliance()
        assert re.search(r"uptime.monitor", content, re.IGNORECASE)
