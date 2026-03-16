"""Tests for backup/recovery documentation and script.

Validates that backup infrastructure exists and meets SOC2 CC6.1 requirements.
"""

import re
import stat
from functools import cache
from pathlib import Path

PROJ_DIR = Path(__file__).resolve().parents[3]
DOCS_DIR = PROJ_DIR / "docs"
SCRIPTS_DIR = PROJ_DIR / "scripts"
BACKUP_SCRIPT = SCRIPTS_DIR / "backup.sh"
BACKUP_DOC = DOCS_DIR / "BACKUP-RECOVERY.md"
COMPLIANCE_DOC = DOCS_DIR / "COMPLIANCE.md"


class TestBackupScriptExists:
    """AC: Automated backup mechanism exists."""

    def test_backup_script_exists(self) -> None:
        assert BACKUP_SCRIPT.is_file()

    def test_backup_script_is_executable(self) -> None:
        mode = BACKUP_SCRIPT.stat().st_mode
        assert mode & stat.S_IXUSR, "backup.sh must be executable"


@cache
def _read_script() -> str:
    return BACKUP_SCRIPT.read_text()


@cache
def _read_doc() -> str:
    return BACKUP_DOC.read_text()


class TestBackupScriptContent:
    """AC: Script uses sqlite3 .backup, includes error handling and logging."""

    def test_uses_sqlite3_backup(self) -> None:
        content = _read_script()
        assert ".backup" in content, (
            "Script must use sqlite3 .backup for consistent snapshots"
        )

    def test_has_error_handling(self) -> None:
        content = _read_script()
        assert "set -e" in content or "trap" in content or "|| {" in content

    def test_has_logging(self) -> None:
        content = _read_script()
        assert re.search(r"log|echo.*\[", content, re.IGNORECASE)

    def test_has_retention_policy(self) -> None:
        content = _read_script()
        assert re.search(
            r"retain|prune|cleanup|remove.*old|keep.*last", content, re.IGNORECASE
        )

    def test_has_timestamp_in_filename(self) -> None:
        content = _read_script()
        assert re.search(r"date|timestamp|\$\(date", content)


class TestBackupRecoveryDoc:
    """AC: docs/BACKUP-RECOVERY.md covers strategy, targets, restore, monitoring."""

    def test_doc_exists(self) -> None:
        assert BACKUP_DOC.is_file()

    def test_rpo_documented(self) -> None:
        content = _read_doc()
        assert re.search(r"RPO", content)

    def test_rto_documented(self) -> None:
        content = _read_doc()
        assert re.search(r"RTO", content)

    def test_rpo_target_under_1_hour(self) -> None:
        content = _read_doc()
        assert re.search(r"RPO.*<?\s*1\s*hour|RPO.*60\s*min", content, re.IGNORECASE)

    def test_rto_target_under_4_hours(self) -> None:
        content = _read_doc()
        assert re.search(r"RTO.*<?\s*4\s*hour", content, re.IGNORECASE)

    def test_restore_procedure_section(self) -> None:
        content = _read_doc()
        assert re.search(r"#+\s+.*restore", content, re.IGNORECASE)

    def test_restore_mentions_integrity_check(self) -> None:
        content = _read_doc()
        assert "integrity_check" in content

    def test_backup_strategy_section(self) -> None:
        content = _read_doc()
        assert re.search(r"#+\s+.*strateg", content, re.IGNORECASE)

    def test_monitoring_section(self) -> None:
        content = _read_doc()
        assert re.search(r"#+\s+.*monitor", content, re.IGNORECASE)


class TestComplianceUpdated:
    """AC: COMPLIANCE.md updated for CC6.1."""

    def test_cc61_references_backup_doc(self) -> None:
        content = COMPLIANCE_DOC.read_text()
        assert "BACKUP-RECOVERY" in content
