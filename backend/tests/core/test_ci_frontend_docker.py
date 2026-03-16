"""Tests for frontend Docker build verification in CI.

Validates that ci.yml includes a frontend Docker build job with
caching, no push, and reasonable timeout.
"""

import re
from functools import cache
from pathlib import Path

import yaml

CI_WORKFLOW = Path(__file__).resolve().parents[3] / ".github" / "workflows" / "ci.yml"


@cache
def _load_ci() -> dict:
    return yaml.safe_load(CI_WORKFLOW.read_text())


class TestFrontendDockerJob:
    """AC: Frontend Docker build job exists in ci.yml."""

    def test_frontend_docker_job_exists(self) -> None:
        ci = _load_ci()
        jobs = ci.get("jobs", {})
        docker_fe = [
            k for k in jobs if "docker" in k.lower() and "frontend" in k.lower()
        ]
        assert len(docker_fe) >= 1, f"No frontend Docker job. Jobs: {list(jobs.keys())}"

    def test_job_runs_on_pr(self) -> None:
        """AC: Builds on every PR."""
        ci = _load_ci()
        on = ci.get("on", ci.get(True, {}))
        assert "pull_request" in on

    def test_job_has_timeout(self) -> None:
        """AC: Reasonable timeout."""
        ci = _load_ci()
        jobs = ci.get("jobs", {})
        job = next(
            (
                v
                for k, v in jobs.items()
                if "docker" in k.lower() and "frontend" in k.lower()
            ),
            None,
        )
        assert job is not None
        assert "timeout-minutes" in job

    def test_does_not_push(self) -> None:
        """AC: Build only, no push."""
        # The frontend docker section should have push: false or no push at all
        # Check that build-push-action uses push: false, or plain docker build (no push)
        ci = _load_ci()
        jobs = ci.get("jobs", {})
        job = next(
            (
                v
                for k, v in jobs.items()
                if "docker" in k.lower() and "frontend" in k.lower()
            ),
            None,
        )
        assert job is not None
        steps_yaml = yaml.dump(job.get("steps", []))
        if "build-push-action" in steps_yaml:
            assert "push: false" in steps_yaml or "push: 'false'" in steps_yaml
        else:
            # Plain docker build — no push command
            assert "docker push" not in steps_yaml

    def test_has_layer_caching(self) -> None:
        """AC: Docker layer caching configured."""
        ci = _load_ci()
        jobs = ci.get("jobs", {})
        job = next(
            (
                v
                for k, v in jobs.items()
                if "docker" in k.lower() and "frontend" in k.lower()
            ),
            None,
        )
        assert job is not None
        steps_yaml = yaml.dump(job.get("steps", []))
        assert re.search(r"cache|buildx", steps_yaml, re.IGNORECASE)

    def test_builds_frontend_context(self) -> None:
        """Builds from frontend/ directory."""
        ci = _load_ci()
        jobs = ci.get("jobs", {})
        job = next(
            (
                v
                for k, v in jobs.items()
                if "docker" in k.lower() and "frontend" in k.lower()
            ),
            None,
        )
        assert job is not None
        steps_yaml = yaml.dump(job.get("steps", []))
        assert "frontend" in steps_yaml
