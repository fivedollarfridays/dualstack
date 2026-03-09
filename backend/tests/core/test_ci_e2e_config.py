"""Tests for CI pipeline E2E test configuration.

Validates that the GitHub Actions CI workflow includes a Playwright E2E job
with proper browser installation, artifact upload, and timeout settings.
"""

import re
from functools import cache
from pathlib import Path

import yaml

PROJ_DIR = Path(__file__).resolve().parents[3]
CI_WORKFLOW = PROJ_DIR / ".github" / "workflows" / "ci.yml"
PLAYWRIGHT_CONFIG = PROJ_DIR / "frontend" / "playwright.config.ts"


@cache
def _load_ci() -> dict:
    return yaml.safe_load(CI_WORKFLOW.read_text())


@cache
def _read_config() -> str:
    return PLAYWRIGHT_CONFIG.read_text()


class TestCIWorkflowHasE2EJob:
    """AC: E2E test job exists in .github/workflows/ci.yml."""

    def test_e2e_job_exists(self) -> None:
        ci = _load_ci()
        jobs = ci.get("jobs", {})
        e2e_jobs = [k for k in jobs if "e2e" in k.lower()]
        assert len(e2e_jobs) >= 1, f"No E2E job found in CI. Jobs: {list(jobs.keys())}"

    def test_e2e_job_installs_browsers(self) -> None:
        """AC: Playwright browsers installed with system dependencies."""
        content = CI_WORKFLOW.read_text()
        assert re.search(r"playwright install", content, re.IGNORECASE)

    def test_e2e_job_runs_playwright(self) -> None:
        content = CI_WORKFLOW.read_text()
        assert re.search(r"playwright test", content, re.IGNORECASE)

    def test_e2e_job_uploads_artifacts_on_failure(self) -> None:
        """AC: Test artifacts uploaded on failure."""
        content = CI_WORKFLOW.read_text()
        assert re.search(r"upload-artifact", content)
        assert re.search(r"failure\(\)", content)

    def test_e2e_job_has_timeout(self) -> None:
        """AC: Job has reasonable timeout."""
        ci = _load_ci()
        e2e_jobs = {k: v for k, v in ci.get("jobs", {}).items() if "e2e" in k.lower()}
        for name, job in e2e_jobs.items():
            assert "timeout-minutes" in job, f"E2E job '{name}' missing timeout-minutes"

    def test_e2e_runs_on_pr(self) -> None:
        """AC: E2E tests run on every PR."""
        ci = _load_ci()
        on = ci.get("on", ci.get(True, {}))
        assert "pull_request" in on


class TestPlaywrightConfig:
    """AC: playwright.config.ts has CI-compatible settings."""

    def test_ci_retries(self) -> None:
        content = _read_config()
        assert re.search(r"process\.env\.CI.*\?.*2.*:.*0|retries.*CI", content)

    def test_has_web_server(self) -> None:
        content = _read_config()
        assert "webServer" in content

    def test_trace_on_retry(self) -> None:
        content = _read_config()
        assert re.search(r"trace.*on-first-retry|trace.*retain-on-failure", content)

    def test_screenshot_on_failure(self) -> None:
        content = _read_config()
        assert re.search(r"screenshot.*only-on-failure", content)
