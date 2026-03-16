"""Tests for incident response runbook document structure.

Validates that INCIDENT-RESPONSE.md exists and contains all required sections
per SOC2 CC7.2 requirements and task acceptance criteria.
"""

import re
from functools import cache
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parents[3] / "docs"
RUNBOOK_PATH = DOCS_DIR / "INCIDENT-RESPONSE.md"
COMPLIANCE_PATH = DOCS_DIR / "COMPLIANCE.md"


class TestRunbookExists:
    def test_incident_response_file_exists(self) -> None:
        assert RUNBOOK_PATH.is_file()


@cache
def _read_runbook() -> str:
    return RUNBOOK_PATH.read_text()


class TestSeverityLevels:
    """AC: Severity levels (SEV1-SEV4) defined with response time expectations."""

    def test_sev1_defined(self) -> None:
        content = _read_runbook()
        assert "SEV1" in content or "Sev1" in content or "sev1" in content

    def test_sev2_defined(self) -> None:
        content = _read_runbook()
        assert "SEV2" in content or "Sev2" in content or "sev2" in content

    def test_sev3_defined(self) -> None:
        content = _read_runbook()
        assert "SEV3" in content or "sev3" in content

    def test_sev4_defined(self) -> None:
        content = _read_runbook()
        assert "SEV4" in content or "sev4" in content

    def test_response_times_defined(self) -> None:
        content = _read_runbook()
        assert re.search(
            r"response.{0,20}time|acknowledge|minutes|hour", content, re.IGNORECASE
        )


class TestDetection:
    """AC: Detection methods documented referencing Grafana alerts."""

    def test_detection_section_exists(self) -> None:
        content = _read_runbook()
        assert re.search(r"#+\s+.*detection", content, re.IGNORECASE)

    def test_references_grafana(self) -> None:
        content = _read_runbook()
        assert "Grafana" in content or "grafana" in content


class TestTriageProcess:
    """AC: Triage process documented with clear steps."""

    def test_triage_section_exists(self) -> None:
        content = _read_runbook()
        assert re.search(r"#+\s+.*triage", content, re.IGNORECASE)


class TestCommunicationTemplates:
    """AC: Communication templates for internal, external, escalation, resolution."""

    def test_communication_section_exists(self) -> None:
        content = _read_runbook()
        assert re.search(r"#+\s+.*communicat", content, re.IGNORECASE)

    def test_internal_template(self) -> None:
        content = _read_runbook()
        assert re.search(r"internal", content, re.IGNORECASE)

    def test_external_template(self) -> None:
        content = _read_runbook()
        assert re.search(r"external|status.page|customer", content, re.IGNORECASE)

    def test_escalation_template(self) -> None:
        content = _read_runbook()
        assert re.search(r"escalat", content, re.IGNORECASE)

    def test_resolution_template(self) -> None:
        content = _read_runbook()
        assert re.search(r"resolution.{0,30}(template|notif)", content, re.IGNORECASE)


class TestResolutionSteps:
    """AC: Resolution steps cover isolation, diagnosis, fix/rollback, verification."""

    def test_resolution_section_exists(self) -> None:
        content = _read_runbook()
        assert re.search(r"#+\s+.*resolution", content, re.IGNORECASE)

    def test_mentions_rollback(self) -> None:
        content = _read_runbook()
        assert "rollback" in content.lower()


class TestSpecificRunbooks:
    """AC: At least 3 specific runbooks for common incident types."""

    def test_error_rate_runbook(self) -> None:
        content = _read_runbook()
        assert re.search(r"error.rate", content, re.IGNORECASE)

    def test_auth_failure_runbook(self) -> None:
        content = _read_runbook()
        assert re.search(r"auth.{0,20}(fail|service)", content, re.IGNORECASE)

    def test_database_runbook(self) -> None:
        content = _read_runbook()
        assert re.search(r"database", content, re.IGNORECASE)


class TestPostIncidentReview:
    """AC: Post-incident review template with timeline, root cause, impact, action items."""

    def test_post_incident_section_exists(self) -> None:
        content = _read_runbook()
        assert re.search(r"#+\s+.*post.incident", content, re.IGNORECASE)

    def test_mentions_root_cause(self) -> None:
        content = _read_runbook()
        assert re.search(r"root.cause", content, re.IGNORECASE)

    def test_mentions_timeline(self) -> None:
        content = _read_runbook()
        assert re.search(r"timeline", content, re.IGNORECASE)

    def test_mentions_action_items(self) -> None:
        content = _read_runbook()
        assert re.search(r"action.items", content, re.IGNORECASE)


class TestComplianceUpdated:
    """AC: COMPLIANCE.md updated to reflect CC7.2 addressed."""

    def test_cc72_marked_addressed(self) -> None:
        content = COMPLIANCE_PATH.read_text()
        # Should reference the runbook and indicate addressed
        assert re.search(r"INCIDENT-RESPONSE", content)
