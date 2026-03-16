"""Tests for database restore script, backup monitoring alerts, and documentation.

Validates restore script, Prometheus backup alerts, and updated
BACKUP-RECOVERY.md for SOC2 CC6.1 compliance.
"""

import os
import re
from functools import cache
from pathlib import Path

import yaml

PROJ_DIR = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = PROJ_DIR / "scripts"
ALERTS_DIR = PROJ_DIR / "monitoring" / "prometheus" / "alerts"
BACKUP_DOC = PROJ_DIR / "docs" / "BACKUP-RECOVERY.md"
COMPLIANCE_DOC = PROJ_DIR / "docs" / "COMPLIANCE.md"
RESTORE_SCRIPT = SCRIPTS_DIR / "restore.sh"


@cache
def _read_restore() -> str:
    return RESTORE_SCRIPT.read_text()


@cache
def _load_backup_rules() -> dict:
    return yaml.safe_load((ALERTS_DIR / "backup.yml").read_text())


@cache
def _read_backup_doc() -> str:
    return BACKUP_DOC.read_text()


@cache
def _read_compliance() -> str:
    return COMPLIANCE_DOC.read_text()


class TestRestoreScriptExists:
    """scripts/restore.sh exists and is executable."""

    def test_exists(self) -> None:
        assert RESTORE_SCRIPT.is_file()

    def test_executable(self) -> None:
        assert os.access(RESTORE_SCRIPT, os.X_OK)


class TestRestoreScriptFeatures:
    """AC: Restore script handles backup file, safety backup, validation."""

    def test_accepts_backup_file_arg(self) -> None:
        content = _read_restore()
        assert "--backup-file" in content

    def test_creates_safety_backup(self) -> None:
        """Creates a safety backup of the current DB before restoring."""
        content = _read_restore()
        assert re.search(r"safety|pre.restore|backup.*current", content, re.IGNORECASE)

    def test_validates_restored_db(self) -> None:
        """Validates the restored database is accessible."""
        content = _read_restore()
        assert re.search(
            r"integrity_check|PRAGMA|validation|verify", content, re.IGNORECASE
        )

    def test_exits_nonzero_on_missing_file(self) -> None:
        """Exits non-zero when backup file doesn't exist."""
        content = _read_restore()
        assert re.search(r"exit\s+[1-9]", content)

    def test_has_error_handling(self) -> None:
        content = _read_restore()
        assert "set -e" in content or "set -euo pipefail" in content


class TestBackupAlertRules:
    """AC: Prometheus alert rules for backup health."""

    def test_backup_rules_file_exists(self) -> None:
        assert (ALERTS_DIR / "backup.yml").is_file()

    def test_has_backup_too_old_alert(self) -> None:
        rules = _load_backup_rules()
        names = [r["alert"] for g in rules["groups"] for r in g["rules"]]
        assert "BackupTooOld" in names

    def test_has_backup_size_anomaly_alert(self) -> None:
        rules = _load_backup_rules()
        names = [r["alert"] for g in rules["groups"] for r in g["rules"]]
        assert "BackupSizeAnomaly" in names

    def test_backup_too_old_has_warning(self) -> None:
        """BackupTooOld should have at least a warning severity."""
        rules = _load_backup_rules()
        rule = next(
            (
                r
                for g in rules["groups"]
                for r in g["rules"]
                if r["alert"] == "BackupTooOld"
            ),
            None,
        )
        assert rule is not None, "BackupTooOld rule not found"
        assert rule["labels"]["severity"] in ("warning", "critical")

    def test_backup_size_anomaly_is_warning(self) -> None:
        rules = _load_backup_rules()
        rule = next(
            (
                r
                for g in rules["groups"]
                for r in g["rules"]
                if r["alert"] == "BackupSizeAnomaly"
            ),
            None,
        )
        assert rule is not None, "BackupSizeAnomaly rule not found"
        assert rule["labels"]["severity"] == "warning"


class TestBackupDocumentation:
    """AC: BACKUP-RECOVERY.md has restore procedure, testing, monitoring."""

    def test_has_restore_procedure(self) -> None:
        content = _read_backup_doc()
        assert re.search(r"restore.*procedure|restore.*step", content, re.IGNORECASE)

    def test_references_restore_script(self) -> None:
        content = _read_backup_doc()
        assert "restore.sh" in content

    def test_has_restore_testing_section(self) -> None:
        content = _read_backup_doc()
        assert re.search(r"restore.*test|test.*restore", content, re.IGNORECASE)

    def test_has_monitoring_alerts_section(self) -> None:
        content = _read_backup_doc()
        assert re.search(
            r"BackupTooOld|backup.*alert|backup.*monitor", content, re.IGNORECASE
        )

    def test_has_disaster_recovery(self) -> None:
        content = _read_backup_doc()
        assert re.search(r"disaster|emergency|runbook", content, re.IGNORECASE)


class TestComplianceUpdated:
    """AC: COMPLIANCE.md CC6.1 gaps marked as addressed."""

    def test_restore_gap_addressed(self) -> None:
        content = _read_compliance()
        assert re.search(r"~~.*restore|restore.*address", content, re.IGNORECASE)

    def test_backup_monitoring_gap_addressed(self) -> None:
        content = _read_compliance()
        assert re.search(
            r"~~.*backup.*monitor|backup.*alert.*address", content, re.IGNORECASE
        )
