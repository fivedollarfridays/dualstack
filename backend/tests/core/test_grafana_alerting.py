"""Tests for Grafana alerting provisioning configuration.

Validates that the Grafana provisioning YAML files exist, are valid YAML,
and contain the required alert rules, contact points, and notification policies.
"""

from pathlib import Path

import pytest
import yaml

MONITORING_DIR = Path(__file__).resolve().parents[3] / "monitoring"
ALERTING_DIR = MONITORING_DIR / "grafana" / "provisioning" / "alerting"


class TestAlertingProvisioningFilesExist:
    """All required provisioning files must exist."""

    def test_rules_yaml_exists(self) -> None:
        assert (ALERTING_DIR / "rules.yaml").is_file()

    def test_contactpoints_yaml_exists(self) -> None:
        assert (ALERTING_DIR / "contactpoints.yaml").is_file()

    def test_policies_yaml_exists(self) -> None:
        assert (ALERTING_DIR / "policies.yaml").is_file()


def _load_yaml(filename: str) -> dict:
    path = ALERTING_DIR / filename
    return yaml.safe_load(path.read_text())


class TestAlertRules:
    """Alert rules provisioning file structure and content."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.data = _load_yaml("rules.yaml")

    def test_api_version(self) -> None:
        assert self.data["apiVersion"] == 1

    def test_has_groups(self) -> None:
        assert "groups" in self.data
        assert len(self.data["groups"]) >= 1

    def test_all_groups_have_folder(self) -> None:
        for group in self.data["groups"]:
            assert "folder" in group

    def test_all_groups_have_rules(self) -> None:
        for group in self.data["groups"]:
            assert "rules" in group
            assert len(group["rules"]) >= 1

    def _find_rule(self, title_fragment: str) -> dict | None:
        for group in self.data["groups"]:
            for rule in group["rules"]:
                if title_fragment.lower() in rule["title"].lower():
                    return rule
        return None

    def test_error_rate_rule_exists(self) -> None:
        rule = self._find_rule("error rate")
        assert rule is not None, "No alert rule with 'error rate' in title"

    def test_auth_failure_rule_exists(self) -> None:
        rule = self._find_rule("auth")
        assert rule is not None, "No alert rule with 'auth' in title"

    def test_latency_rule_exists(self) -> None:
        rule = self._find_rule("latency")
        assert rule is not None, "No alert rule with 'latency' in title"

    def test_rules_have_required_fields(self) -> None:
        for group in self.data["groups"]:
            for rule in group["rules"]:
                assert "uid" in rule, f"Rule '{rule.get('title')}' missing uid"
                assert "title" in rule, "Rule missing title"
                assert "condition" in rule, f"Rule '{rule['title']}' missing condition"
                assert "data" in rule, f"Rule '{rule['title']}' missing data"
                assert "for" in rule, f"Rule '{rule['title']}' missing 'for' duration"

    def test_rules_have_severity_label(self) -> None:
        for group in self.data["groups"]:
            for rule in group["rules"]:
                labels = rule.get("labels", {})
                assert "severity" in labels, (
                    f"Rule '{rule['title']}' missing severity label"
                )

    def test_rules_have_annotations(self) -> None:
        for group in self.data["groups"]:
            for rule in group["rules"]:
                annotations = rule.get("annotations", {})
                assert "summary" in annotations, (
                    f"Rule '{rule['title']}' missing summary annotation"
                )


class TestContactPoints:
    """Contact points provisioning file structure and content."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.data = _load_yaml("contactpoints.yaml")

    def test_api_version(self) -> None:
        assert self.data["apiVersion"] == 1

    def test_has_contact_points(self) -> None:
        assert "contactPoints" in self.data
        assert len(self.data["contactPoints"]) >= 1

    def test_contact_point_has_name(self) -> None:
        for cp in self.data["contactPoints"]:
            assert "name" in cp

    def test_contact_point_has_receivers(self) -> None:
        for cp in self.data["contactPoints"]:
            assert "receivers" in cp
            assert len(cp["receivers"]) >= 1

    def test_receivers_have_required_fields(self) -> None:
        for cp in self.data["contactPoints"]:
            for receiver in cp["receivers"]:
                assert "uid" in receiver, "Receiver missing uid"
                assert "type" in receiver, "Receiver missing type"
                assert "settings" in receiver, "Receiver missing settings"


class TestNotificationPolicies:
    """Notification policies provisioning file structure and content."""

    @pytest.fixture(autouse=True)
    def _load(self) -> None:
        self.data = _load_yaml("policies.yaml")

    def test_api_version(self) -> None:
        assert self.data["apiVersion"] == 1

    def test_has_policies(self) -> None:
        assert "policies" in self.data
        assert len(self.data["policies"]) >= 1

    def test_policy_has_receiver(self) -> None:
        for policy in self.data["policies"]:
            assert "receiver" in policy

    def test_policy_groups_by_alertname(self) -> None:
        policy = self.data["policies"][0]
        group_by = policy.get("group_by", [])
        assert "alertname" in group_by


class TestDatasourceUid:
    """Datasource provisioning must include a stable UID for alert rule references."""

    def test_prometheus_datasource_has_uid(self) -> None:
        ds_path = (
            MONITORING_DIR
            / "grafana"
            / "provisioning"
            / "datasources"
            / "prometheus.yml"
        )
        data = yaml.safe_load(ds_path.read_text())
        ds = data["datasources"][0]
        assert "uid" in ds, (
            "Prometheus datasource must have a stable uid for alert rules"
        )
        assert ds["uid"] == "prometheus"
