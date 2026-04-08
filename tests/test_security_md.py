"""Validate SECURITY.md exists, is within target length, and has required sections."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SECURITY_MD = REPO_ROOT / "SECURITY.md"

REQUIRED_SECTIONS = [
    "Content Security Policy",
    "Authentication",
    "Authorization",
    "Input Validation",
    "Rate Limiting",
    "Webhook Security",
    "File Upload Security",
    "Audit Logging",
    "Cookie Security",
    "WebSocket Security",
]


def test_security_md_exists() -> None:
    assert SECURITY_MD.exists(), "SECURITY.md must exist at repo root"


def test_security_md_length() -> None:
    lines = SECURITY_MD.read_text().splitlines()
    assert 90 <= len(lines) <= 140, f"Expected 90-140 lines, got {len(lines)}"


def test_security_md_has_required_sections() -> None:
    content = SECURITY_MD.read_text()
    for section in REQUIRED_SECTIONS:
        assert section in content, f"Missing required section: {section}"


def test_security_md_no_marketing_language() -> None:
    content = SECURITY_MD.read_text().lower()
    marketing_terms = ["best-in-class", "world-class", "cutting-edge", "state-of-the-art"]
    for term in marketing_terms:
        assert term not in content, f"Marketing language found: {term}"


def test_security_md_references_source_files() -> None:
    content = SECURITY_MD.read_text()
    expected_paths = [
        "backend/app/core/auth.py",
        "backend/app/core/rbac.py",
        "backend/app/core/security_headers.py",
        "frontend/src/lib/csp.ts",
    ]
    for path in expected_paths:
        assert path in content, f"Missing source file reference: {path}"
