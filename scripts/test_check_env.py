"""Tests for check_env.py — environment variable validation."""

import os
import tempfile
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Cycle 1: Core validation — required var present / missing
# ---------------------------------------------------------------------------


class TestCheckSingleVar:
    """Validate a single required variable."""

    def test_required_var_present_passes(self):
        from check_env import check_var

        result = check_var("MY_VAR", "some-real-value", required=True)
        assert result.status == "PASS"

    def test_required_var_missing_fails(self):
        from check_env import check_var

        result = check_var("MY_VAR", "", required=True)
        assert result.status == "FAIL"

    def test_required_var_none_fails(self):
        from check_env import check_var

        result = check_var("MY_VAR", None, required=True)
        assert result.status == "FAIL"


# ---------------------------------------------------------------------------
# Cycle 2: Placeholder detection
# ---------------------------------------------------------------------------


class TestPlaceholderDetection:
    """Reject known placeholder values for required vars."""

    @pytest.mark.parametrize(
        "value",
        [
            "your-key-here",
            "changeme",
            "pk_test_placeholder",
            "sk_test_xxx",
            "YOUR_KEY_HERE",
            "CHANGEME",
        ],
    )
    def test_placeholder_value_fails(self, value: str):
        from check_env import check_var

        result = check_var("MY_VAR", value, required=True)
        assert result.status == "FAIL"
        assert "placeholder" in result.message.lower()

    def test_real_value_passes(self):
        from check_env import check_var

        result = check_var("MY_VAR", "sk_test_realkey123abc", required=True)
        assert result.status == "PASS"


# ---------------------------------------------------------------------------
# Cycle 3: Optional var warnings
# ---------------------------------------------------------------------------


class TestOptionalVars:
    """Optional vars warn when empty, pass when set."""

    def test_optional_var_empty_warns(self):
        from check_env import check_var

        result = check_var("RESEND_API_KEY", "", required=False)
        assert result.status == "WARN"

    def test_optional_var_set_passes(self):
        from check_env import check_var

        result = check_var("RESEND_API_KEY", "re_abc123", required=False)
        assert result.status == "PASS"


# ---------------------------------------------------------------------------
# Cycle 4: Database URL special case
# ---------------------------------------------------------------------------


class TestDatabaseUrlGroup:
    """At least one of DATABASE_URL or TURSO_DATABASE_URL must be set."""

    def test_both_missing_fails(self):
        from check_env import check_database_url

        result = check_database_url(database_url="", turso_database_url="")
        assert result.status == "FAIL"

    def test_database_url_only_passes(self):
        from check_env import check_database_url

        result = check_database_url(
            database_url="postgresql+asyncpg://u:p@host/db",
            turso_database_url="",
        )
        assert result.status == "PASS"

    def test_turso_url_only_passes(self):
        from check_env import check_database_url

        result = check_database_url(
            database_url="",
            turso_database_url="file:local.db",
        )
        assert result.status == "PASS"

    def test_both_set_passes(self):
        from check_env import check_database_url

        result = check_database_url(
            database_url="postgresql+asyncpg://u:p@host/db",
            turso_database_url="file:local.db",
        )
        assert result.status == "PASS"


# ---------------------------------------------------------------------------
# Cycle 5: Env file parsing
# ---------------------------------------------------------------------------


class TestParseEnvFile:
    """Read a .env file and return a dict of key=value pairs."""

    def test_parse_valid_env_file(self, tmp_path: Path):
        from check_env import parse_env_file

        env_file = tmp_path / ".env"
        env_file.write_text("FOO=bar\nBAZ=qux\n")
        result = parse_env_file(str(env_file))
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_parse_file_with_comments(self, tmp_path: Path):
        from check_env import parse_env_file

        env_file = tmp_path / ".env"
        env_file.write_text("# comment\nFOO=bar\n# another\n")
        result = parse_env_file(str(env_file))
        assert result == {"FOO": "bar"}

    def test_parse_file_with_empty_lines(self, tmp_path: Path):
        from check_env import parse_env_file

        env_file = tmp_path / ".env"
        env_file.write_text("FOO=bar\n\nBAZ=qux\n")
        result = parse_env_file(str(env_file))
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_parse_missing_file_returns_none(self, tmp_path: Path):
        from check_env import parse_env_file

        result = parse_env_file(str(tmp_path / "nonexistent"))
        assert result is None

    def test_parse_value_with_equals(self, tmp_path: Path):
        from check_env import parse_env_file

        env_file = tmp_path / ".env"
        env_file.write_text("DATABASE_URL=postgres://u:p=123@host/db\n")
        result = parse_env_file(str(env_file))
        assert result == {"DATABASE_URL": "postgres://u:p=123@host/db"}


# ---------------------------------------------------------------------------
# Cycle 6: Full validation run
# ---------------------------------------------------------------------------


class TestValidateAll:
    """Integration: validate_all returns list of CheckResults and exit code."""

    def test_all_required_vars_set_returns_zero(self, tmp_path: Path):
        from check_env import validate_all

        backend_env = tmp_path / "backend" / ".env"
        backend_env.parent.mkdir(parents=True)
        backend_env.write_text(
            "DATABASE_URL=postgresql+asyncpg://u:p@host/db\n"
            "CLERK_JWKS_URL=https://clerk.example.com/.well-known/jwks.json\n"
            "STRIPE_SECRET_KEY=sk_test_realkey123abc\n"
            "STRIPE_WEBHOOK_SECRET=whsec_realkey123abc\n"
            "METRICS_API_KEY=a1b2c3d4e5f6g7h8i9j0\n"
        )
        frontend_env = tmp_path / "frontend" / ".env.local"
        frontend_env.parent.mkdir(parents=True)
        frontend_env.write_text(
            "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_realkey123\n"
            "NEXT_PUBLIC_API_URL=http://localhost:8000\n"
        )

        results, exit_code = validate_all(str(tmp_path))
        assert exit_code == 0
        fail_names = [r.name for r in results if r.status == "FAIL"]
        assert fail_names == [], f"Unexpected failures: {fail_names}"

    def test_missing_required_var_returns_one(self, tmp_path: Path):
        from check_env import validate_all

        backend_env = tmp_path / "backend" / ".env"
        backend_env.parent.mkdir(parents=True)
        backend_env.write_text("TURSO_DATABASE_URL=file:local.db\n")
        frontend_env = tmp_path / "frontend" / ".env.local"
        frontend_env.parent.mkdir(parents=True)
        frontend_env.write_text("")

        results, exit_code = validate_all(str(tmp_path))
        assert exit_code == 1

    def test_missing_env_file_returns_one(self, tmp_path: Path):
        from check_env import validate_all

        # No files at all
        results, exit_code = validate_all(str(tmp_path))
        assert exit_code == 1
