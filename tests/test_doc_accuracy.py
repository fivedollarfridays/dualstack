"""Doc accuracy tests — validates README.md and LISTING.md claims.

Ensures no stale Drizzle references, correct test counts, and qualified
email feature descriptions across documentation files.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestReadmeNoDrizzle:
    """Verify all Drizzle ORM references have been removed from README."""

    def test_readme_no_drizzle_references(self) -> None:
        text = (ROOT / "README.md").read_text()
        assert "drizzle" not in text.lower(), (
            "README.md must not reference Drizzle ORM (stale dependency)"
        )

    def test_readme_no_nonexistent_dirs(self) -> None:
        text = (ROOT / "README.md").read_text()
        # Project structure section should not mention Drizzle-related dirs
        assert "Drizzle + Turso" not in text, (
            "README.md must not reference 'Drizzle + Turso' directory comment"
        )
        assert "Frontend migrations" not in text, (
            "README.md must not reference 'Frontend migrations' directory"
        )


class TestReadmeTestCounts:
    """Verify README test counts match current numbers."""

    def test_readme_test_count_badge(self) -> None:
        text = (ROOT / "README.md").read_text()
        # Badge line uses format: tests-NNNN_passing
        assert "tests-1357_passing" in text, (
            "README badge must show 1357 tests passing"
        )

    def test_readme_test_count_backend(self) -> None:
        text = (ROOT / "README.md").read_text()
        assert "863 tests" in text, (
            "README must reference 863 backend tests"
        )

    def test_readme_test_count_frontend(self) -> None:
        text = (ROOT / "README.md").read_text()
        assert "494 tests" in text, (
            "README must reference 494 frontend tests"
        )


class TestListingTestCounts:
    """Verify LISTING.md test counts match current numbers."""

    def test_listing_test_count_total(self) -> None:
        text = (ROOT / "badges" / "LISTING.md").read_text()
        assert "1,357" in text, (
            "LISTING.md must reference 1,357 total tests"
        )

    def test_listing_test_count_frontend(self) -> None:
        text = (ROOT / "badges" / "LISTING.md").read_text()
        assert "494 frontend" in text, (
            "LISTING.md must reference 494 frontend tests"
        )


class TestEmailFeatureQualified:
    """Verify email feature is described as infrastructure-ready."""

    def test_email_feature_qualified_readme(self) -> None:
        text = (ROOT / "README.md").read_text()
        # Find the email line and check it contains "infrastructure"
        email_lines = [
            line for line in text.splitlines()
            if "email" in line.lower() and "resend" in line.lower()
        ]
        assert any("infrastructure" in line.lower() for line in email_lines), (
            "README email feature must be qualified as infrastructure-ready"
        )

    def test_email_feature_qualified_listing(self) -> None:
        text = (ROOT / "badges" / "LISTING.md").read_text()
        email_lines = [
            line for line in text.splitlines()
            if "email" in line.lower() and "resend" in line.lower()
        ]
        assert any("infrastructure" in line.lower() for line in email_lines), (
            "LISTING.md email feature must be qualified as infrastructure-ready"
        )
