#!/usr/bin/env python3
"""Validate DualStack environment variables before first run.

Usage:
    python3 scripts/check_env.py
    python3 scripts/check_env.py /path/to/project/root

No dependencies beyond the Python standard library.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLACEHOLDER_PATTERNS: tuple[str, ...] = (
    "your-key-here",
    "changeme",
    "pk_test_placeholder",
    "sk_test_xxx",
    "your_key_here",
)

BACKEND_REQUIRED: list[str] = [
    "CLERK_JWKS_URL",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "METRICS_API_KEY",
]

FRONTEND_REQUIRED: list[str] = [
    "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
    "NEXT_PUBLIC_API_URL",
]

OPTIONAL_VARS: list[str] = [
    "RESEND_API_KEY",
    "STORAGE_BUCKET",
    "STORAGE_ACCESS_KEY",
    "STORAGE_SECRET_KEY",
    "CORS_ORIGINS",
]

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    """Result of checking a single env var."""

    name: str
    status: str  # "PASS", "FAIL", "WARN"
    message: str


# ---------------------------------------------------------------------------
# Core checking logic
# ---------------------------------------------------------------------------


def _is_placeholder(value: str) -> bool:
    """Return True if value looks like a placeholder."""
    lower = value.strip().lower()
    for pattern in PLACEHOLDER_PATTERNS:
        if lower == pattern:
            return True
    return False


def check_var(name: str, value: str | None, *, required: bool) -> CheckResult:
    """Check a single environment variable.

    Args:
        name: Variable name.
        value: Variable value (may be None or empty).
        required: Whether the var is required.

    Returns:
        CheckResult with PASS, FAIL, or WARN status.
    """
    if value is None or value.strip() == "":
        if required:
            return CheckResult(name, "FAIL", f"{name} is required but not set")
        return CheckResult(name, "WARN", f"{name} is optional but not set")

    if _is_placeholder(value):
        return CheckResult(name, "FAIL", f"{name} contains a placeholder value")

    return CheckResult(name, "PASS", f"{name} is set")


def check_database_url(
    *, database_url: str, turso_database_url: str
) -> CheckResult:
    """Check that at least one database URL is configured."""
    has_db = database_url.strip() != ""
    has_turso = turso_database_url.strip() != ""

    if not has_db and not has_turso:
        return CheckResult(
            "DATABASE_URL / TURSO_DATABASE_URL",
            "FAIL",
            "At least one database URL must be set",
        )

    label = "DATABASE_URL" if has_db else "TURSO_DATABASE_URL"
    return CheckResult(
        "DATABASE_URL / TURSO_DATABASE_URL",
        "PASS",
        f"Using {label}",
    )


# ---------------------------------------------------------------------------
# Env file parsing
# ---------------------------------------------------------------------------


def parse_env_file(path: str) -> dict[str, str] | None:
    """Parse a .env file into a dict. Returns None if file doesn't exist."""
    file_path = Path(path)
    if not file_path.is_file():
        return None

    env: dict[str, str] = {}
    for line in file_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value
    return env


# ---------------------------------------------------------------------------
# Full validation
# ---------------------------------------------------------------------------


def validate_all(project_root: str) -> tuple[list[CheckResult], int]:
    """Validate all env files and return (results, exit_code)."""
    root = Path(project_root)
    results: list[CheckResult] = []
    has_failure = False

    # -- Backend -----------------------------------------------------------
    backend_env = parse_env_file(str(root / "backend" / ".env"))
    if backend_env is None:
        results.append(
            CheckResult("backend/.env", "FAIL", "File not found")
        )
        has_failure = True
    else:
        # Database URL group check
        db_result = check_database_url(
            database_url=backend_env.get("DATABASE_URL", ""),
            turso_database_url=backend_env.get("TURSO_DATABASE_URL", ""),
        )
        results.append(db_result)
        if db_result.status == "FAIL":
            has_failure = True

        # Required backend vars
        for var in BACKEND_REQUIRED:
            r = check_var(var, backend_env.get(var), required=True)
            results.append(r)
            if r.status == "FAIL":
                has_failure = True

        # Optional vars
        for var in OPTIONAL_VARS:
            r = check_var(var, backend_env.get(var), required=False)
            results.append(r)

    # -- Frontend ----------------------------------------------------------
    frontend_env = parse_env_file(str(root / "frontend" / ".env.local"))
    if frontend_env is None:
        results.append(
            CheckResult("frontend/.env.local", "FAIL", "File not found")
        )
        has_failure = True
    else:
        for var in FRONTEND_REQUIRED:
            r = check_var(var, frontend_env.get(var), required=True)
            results.append(r)
            if r.status == "FAIL":
                has_failure = True

    return results, 1 if has_failure else 0


# ---------------------------------------------------------------------------
# Colorized output
# ---------------------------------------------------------------------------

_COLORS = {
    "PASS": "\033[32m",  # green
    "FAIL": "\033[31m",  # red
    "WARN": "\033[33m",  # yellow
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
}


def _color(status: str) -> str:
    """Return ANSI color code for a status."""
    return _COLORS.get(status, "")


def print_results(results: list[CheckResult]) -> None:
    """Print results with colorized output."""
    reset = _COLORS["RESET"]
    bold = _COLORS["BOLD"]

    print(f"\n{bold}DualStack Environment Check{reset}\n")
    print(f"{'Variable':<45} {'Status':<8} Message")
    print("-" * 80)

    for r in results:
        color = _color(r.status)
        print(f"{r.name:<45} {color}{r.status:<8}{reset} {r.message}")

    # Summary
    passes = sum(1 for r in results if r.status == "PASS")
    fails = sum(1 for r in results if r.status == "FAIL")
    warns = sum(1 for r in results if r.status == "WARN")
    print("-" * 80)
    summary = (
        f"{_COLORS['PASS']}{passes} passed{reset}, "
        f"{_COLORS['FAIL']}{fails} failed{reset}, "
        f"{_COLORS['WARN']}{warns} warnings{reset}"
    )
    print(f"Total: {summary}\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """Run validation and return exit code."""
    project_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    results, exit_code = validate_all(project_root)
    print_results(results)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
