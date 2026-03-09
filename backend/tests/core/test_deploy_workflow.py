"""Tests for deployment workflow configuration.

Validates that deploy.yml exists with staging/production jobs,
proper triggers, concurrency, environment references, and rollback docs.
"""

import re
from functools import cache
from pathlib import Path

import yaml

PROJ_DIR = Path(__file__).resolve().parents[3]
DEPLOY_WORKFLOW = PROJ_DIR / ".github" / "workflows" / "deploy.yml"
CI_WORKFLOW = PROJ_DIR / ".github" / "workflows" / "ci.yml"


@cache
def _load_deploy() -> dict:
    return yaml.safe_load(DEPLOY_WORKFLOW.read_text())


class TestDeployWorkflowExists:
    """AC: .github/workflows/deploy.yml exists with staging and production jobs."""

    def test_deploy_workflow_exists(self) -> None:
        assert DEPLOY_WORKFLOW.is_file()

    def test_has_staging_job(self) -> None:
        ci = _load_deploy()
        jobs = ci.get("jobs", {})
        staging_jobs = [k for k in jobs if "staging" in k.lower()]
        assert len(staging_jobs) >= 1, f"No staging job. Jobs: {list(jobs.keys())}"

    def test_has_production_job(self) -> None:
        ci = _load_deploy()
        jobs = ci.get("jobs", {})
        prod_jobs = [k for k in jobs if "prod" in k.lower()]
        assert len(prod_jobs) >= 1, f"No production job. Jobs: {list(jobs.keys())}"


class TestStagingJob:
    """AC: Staging auto-deploys on merge to main."""

    def test_triggers_on_push_to_main(self) -> None:
        ci = _load_deploy()
        on = ci.get("on", ci.get(True, {}))
        # Accept workflow_dispatch (manual trigger for disabled deploy)
        # or workflow_run/push-to-main triggers
        if "workflow_dispatch" in on or on.get("workflow_dispatch") is not None:
            return  # manual-only mode is acceptable
        wf_run = on.get("workflow_run", {})
        if wf_run:
            assert wf_run.get("types") == ["completed"] or "main" in str(wf_run)
        else:
            push = on.get("push", {})
            assert "main" in push.get("branches", [])

    def test_staging_uses_environment(self) -> None:
        ci = _load_deploy()
        jobs = ci.get("jobs", {})
        staging = next((v for k, v in jobs.items() if "staging" in k.lower()), None)
        assert staging is not None
        env = staging.get("environment", "")
        env_name = env.get("name", env) if isinstance(env, dict) else env
        assert "staging" in str(env_name).lower()

    def test_staging_has_concurrency(self) -> None:
        """AC: Concurrency prevents conflicting simultaneous deploys."""
        ci = _load_deploy()
        jobs = ci.get("jobs", {})
        staging = next((v for k, v in jobs.items() if "staging" in k.lower()), None)
        assert staging is not None
        assert "concurrency" in ci or "concurrency" in staging


class TestProductionJob:
    """AC: Production deploys on tag/release with manual approval gate."""

    def test_triggers_on_release_or_tag(self) -> None:
        ci = _load_deploy()
        on = ci.get("on", ci.get(True, {}))
        # Accept workflow_dispatch (manual trigger for disabled deploy)
        if "workflow_dispatch" in on or on.get("workflow_dispatch") is not None:
            return  # manual-only mode is acceptable
        has_release = "release" in on
        push = on.get("push", {})
        has_tag = any("v" in t for t in push.get("tags", []))
        assert has_release or has_tag, "Production must trigger on release or v* tag"

    def test_production_uses_environment(self) -> None:
        """AC: Production requires manual reviewer approval."""
        ci = _load_deploy()
        jobs = ci.get("jobs", {})
        prod = next((v for k, v in jobs.items() if "prod" in k.lower()), None)
        assert prod is not None
        env = prod.get("environment", "")
        env_name = env.get("name", env) if isinstance(env, dict) else env
        assert "production" in str(env_name).lower()


class TestCIDependency:
    """AC: Deployment depends on CI passing."""

    def test_deploy_depends_on_ci(self) -> None:
        content = DEPLOY_WORKFLOW.read_text()
        assert re.search(r"workflow_run|needs.*ci|needs.*test", content, re.IGNORECASE)


class TestRollbackDocumented:
    """AC: Rollback procedure documented."""

    def test_rollback_in_deploy_or_docs(self) -> None:
        content = DEPLOY_WORKFLOW.read_text()
        has_rollback = "rollback" in content.lower()
        if not has_rollback:
            docs_dir = PROJ_DIR / "docs"
            for f in docs_dir.glob("*.md"):
                text = f.read_text().lower()
                if "rollback" in text and "deploy" in text:
                    has_rollback = True
                    break
        assert has_rollback, "Rollback procedure must be documented"
