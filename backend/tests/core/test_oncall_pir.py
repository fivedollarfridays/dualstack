"""Tests for on-call rotation and post-incident review documentation.

Validates that on-call schedule, escalation matrix, PIR template,
and compliance updates exist for SOC2 CC7.2 compliance.
"""

import re
from functools import cache
from pathlib import Path

PROJ_DIR = Path(__file__).resolve().parents[3]
DOCS_DIR = PROJ_DIR / "docs"
ONCALL_DOC = DOCS_DIR / "ON-CALL.md"
PIR_DOC = DOCS_DIR / "PIR-TEMPLATE.md"
COMPLIANCE_DOC = DOCS_DIR / "COMPLIANCE.md"


@cache
def _read_oncall() -> str:
    return ONCALL_DOC.read_text()


@cache
def _read_pir() -> str:
    return PIR_DOC.read_text()


@cache
def _read_compliance() -> str:
    return COMPLIANCE_DOC.read_text()


class TestOnCallDocExists:
    """ON-CALL.md exists and has required structure."""

    def test_file_exists(self) -> None:
        assert ONCALL_DOC.is_file()


class TestOnCallRotation:
    """AC: Weekly rotation schedule with primary and secondary roles."""

    def test_mentions_weekly_rotation(self) -> None:
        content = _read_oncall()
        assert re.search(r"weekly|rotation", content, re.IGNORECASE)

    def test_has_primary_role(self) -> None:
        content = _read_oncall()
        assert re.search(r"primary", content, re.IGNORECASE)

    def test_has_secondary_role(self) -> None:
        content = _read_oncall()
        assert re.search(r"secondary", content, re.IGNORECASE)


class TestResponseTimeSLAs:
    """AC: Response time SLAs for SEV1-SEV4."""

    def test_has_sev1(self) -> None:
        content = _read_oncall()
        assert re.search(r"SEV1|SEV-1|Sev 1", content)

    def test_has_sev2(self) -> None:
        content = _read_oncall()
        assert re.search(r"SEV2|SEV-2|Sev 2", content)

    def test_has_sev3(self) -> None:
        content = _read_oncall()
        assert re.search(r"SEV3|SEV-3|Sev 3", content)

    def test_has_sev4(self) -> None:
        content = _read_oncall()
        assert re.search(r"SEV4|SEV-4|Sev 4", content)

    def test_mentions_acknowledge_time(self) -> None:
        content = _read_oncall()
        assert re.search(r"acknowledge|ack", content, re.IGNORECASE)


class TestEscalationMatrix:
    """AC: Escalation matrix with severity-based routing and timeframes."""

    def test_mentions_escalation(self) -> None:
        content = _read_oncall()
        assert re.search(r"escalat", content, re.IGNORECASE)

    def test_has_escalation_timeframes(self) -> None:
        """Escalation includes time-based triggers."""
        content = _read_oncall()
        # Should mention minutes for escalation timing
        assert re.search(r"\d+\s*min", content, re.IGNORECASE)


class TestHandoffProcedure:
    """AC: Handoff procedure for rotation transitions."""

    def test_mentions_handoff(self) -> None:
        content = _read_oncall()
        assert re.search(r"handoff|hand-off|handover", content, re.IGNORECASE)


class TestPIRDocExists:
    """PIR-TEMPLATE.md exists."""

    def test_file_exists(self) -> None:
        assert PIR_DOC.is_file()


class TestPIRSections:
    """AC: PIR template includes all required sections."""

    def test_has_metadata(self) -> None:
        content = _read_pir()
        assert re.search(r"metadata|incident.id|date|severity", content, re.IGNORECASE)

    def test_has_timeline(self) -> None:
        content = _read_pir()
        assert re.search(r"timeline", content, re.IGNORECASE)

    def test_has_impact(self) -> None:
        content = _read_pir()
        assert re.search(r"impact", content, re.IGNORECASE)

    def test_has_root_cause(self) -> None:
        content = _read_pir()
        assert re.search(r"root.cause", content, re.IGNORECASE)

    def test_has_contributing_factors(self) -> None:
        content = _read_pir()
        assert re.search(r"contributing.factor", content, re.IGNORECASE)

    def test_has_what_went_well(self) -> None:
        content = _read_pir()
        assert re.search(r"what.went.well", content, re.IGNORECASE)

    def test_has_action_items(self) -> None:
        content = _read_pir()
        assert re.search(r"action.item", content, re.IGNORECASE)

    def test_has_lessons_learned(self) -> None:
        content = _read_pir()
        assert re.search(r"lessons.learned", content, re.IGNORECASE)


class TestPIRCadence:
    """AC: PIR cadence defined (required for SEV1/SEV2)."""

    def test_cadence_defined(self) -> None:
        content = _read_pir()
        assert re.search(r"cadence|requir|mandator", content, re.IGNORECASE)

    def test_sev1_sev2_required(self) -> None:
        content = _read_pir()
        assert re.search(r"SEV1", content) and re.search(r"SEV2", content)

    def test_sev3_optional(self) -> None:
        content = _read_pir()
        assert re.search(r"SEV3", content)


class TestComplianceUpdated:
    """AC: COMPLIANCE.md CC7.2 gaps marked as addressed."""

    def test_oncall_gap_addressed(self) -> None:
        content = _read_compliance()
        assert re.search(r"on.call.*address|~~.*on.call", content, re.IGNORECASE)

    def test_pir_gap_addressed(self) -> None:
        content = _read_compliance()
        assert re.search(
            r"post.incident.*address|~~.*post.incident|PIR.*address|~~.*PIR",
            content,
            re.IGNORECASE,
        )
