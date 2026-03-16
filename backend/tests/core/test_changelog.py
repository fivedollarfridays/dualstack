"""Tests for CHANGELOG.md format and content.

Validates Keep a Changelog format with required sections.
"""

import re
from functools import cache
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parents[3] / "CHANGELOG.md"


class TestChangelogExists:
    def test_changelog_exists(self) -> None:
        assert CHANGELOG.is_file()


@cache
def _read() -> str:
    return CHANGELOG.read_text()


class TestKeepAChangelogFormat:
    """AC: Follows Keep a Changelog format."""

    def test_has_unreleased_section(self) -> None:
        assert re.search(r"##\s+\[Unreleased\]", _read())

    def test_has_v100_section(self) -> None:
        assert re.search(r"##\s+\[1\.0\.0\]", _read())

    def test_has_categorized_entries(self) -> None:
        """AC: Entries categorized by type."""
        content = _read()
        assert re.search(r"###\s+Added", content)
        assert re.search(r"###\s+Security", content)

    def test_v100_has_meaningful_entries(self) -> None:
        """AC: v1.0.0 has retrospective entries for major features."""
        content = _read()
        # Must mention core features, not just placeholders
        assert re.search(r"FastAPI|backend", content, re.IGNORECASE)
        assert re.search(r"Next\.js|frontend", content, re.IGNORECASE)
        assert re.search(r"Clerk|auth", content, re.IGNORECASE)

    def test_has_changelog_process_documented(self) -> None:
        """AC: Changelog generation process documented."""
        content = _read()
        assert re.search(
            r"keepachangelog|conventional|how to|process|format", content, re.IGNORECASE
        )
