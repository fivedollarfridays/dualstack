"""Tests for T22.4 (pre-commit hooks) and T22.5 (dependabot auto-merge + badge)."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


class TestPreCommitConfig:
    """Validate .pre-commit-config.yaml structure and content."""

    def setup_method(self) -> None:
        config_path = ROOT / ".pre-commit-config.yaml"
        assert config_path.exists(), ".pre-commit-config.yaml must exist"
        self.config = yaml.safe_load(config_path.read_text())

    def test_has_repos(self) -> None:
        assert "repos" in self.config
        assert len(self.config["repos"]) >= 2

    def test_pre_commit_hooks_repo(self) -> None:
        repos = {r["repo"]: r for r in self.config["repos"]}
        repo = repos.get("https://github.com/pre-commit/pre-commit-hooks")
        assert repo is not None, "pre-commit-hooks repo must be configured"
        hook_ids = [h["id"] for h in repo["hooks"]]
        assert "trailing-whitespace" in hook_ids
        assert "end-of-file-fixer" in hook_ids
        assert "check-yaml" in hook_ids
        assert "check-added-large-files" in hook_ids

    def test_large_files_max_500kb(self) -> None:
        repos = {r["repo"]: r for r in self.config["repos"]}
        repo = repos["https://github.com/pre-commit/pre-commit-hooks"]
        large_files_hook = next(
            h for h in repo["hooks"] if h["id"] == "check-added-large-files"
        )
        assert "--maxkb=500" in large_files_hook["args"]

    def test_ruff_repo(self) -> None:
        repos = {r["repo"]: r for r in self.config["repos"]}
        repo = repos.get("https://github.com/astral-sh/ruff-pre-commit")
        assert repo is not None, "ruff-pre-commit repo must be configured"
        hook_ids = [h["id"] for h in repo["hooks"]]
        assert "ruff" in hook_ids
        assert "ruff-format" in hook_ids

    def test_ruff_fix_flag(self) -> None:
        repos = {r["repo"]: r for r in self.config["repos"]}
        repo = repos["https://github.com/astral-sh/ruff-pre-commit"]
        ruff_hook = next(h for h in repo["hooks"] if h["id"] == "ruff")
        assert "--fix" in ruff_hook["args"]


class TestDependabotAutoMerge:
    """Validate dependabot-auto-merge.yml workflow."""

    def setup_method(self) -> None:
        workflow_path = (
            ROOT / ".github" / "workflows" / "dependabot-auto-merge.yml"
        )
        assert workflow_path.exists(), "dependabot-auto-merge.yml must exist"
        self.workflow = yaml.safe_load(workflow_path.read_text())

    def test_triggers_on_pull_request(self) -> None:
        # YAML parses 'on' as True (boolean); use True key
        assert self.workflow[True] == "pull_request"

    def test_has_required_permissions(self) -> None:
        perms = self.workflow["permissions"]
        assert perms["contents"] == "write"
        assert perms["pull-requests"] == "write"

    def test_job_checks_dependabot_actor(self) -> None:
        job = self.workflow["jobs"]["auto-merge"]
        assert "dependabot[bot]" in job["if"]

    def test_uses_fetch_metadata(self) -> None:
        steps = self.workflow["jobs"]["auto-merge"]["steps"]
        fetch_step = steps[0]
        assert "dependabot/fetch-metadata" in fetch_step["uses"]

    def test_only_merges_patch_updates(self) -> None:
        steps = self.workflow["jobs"]["auto-merge"]["steps"]
        merge_step = steps[1]
        assert "semver-patch" in merge_step["if"]


class TestMakefileTargets:
    """Validate Makefile has lint and format targets."""

    def setup_method(self) -> None:
        makefile_path = ROOT / "Makefile"
        self.content = makefile_path.read_text()

    def test_lint_target_exists(self) -> None:
        assert "lint:" in self.content

    def test_lint_runs_ruff(self) -> None:
        assert "ruff check" in self.content

    def test_lint_runs_eslint(self) -> None:
        assert "pnpm lint" in self.content

    def test_format_target_exists(self) -> None:
        assert "format:" in self.content

    def test_format_runs_ruff_format(self) -> None:
        assert "ruff format" in self.content


class TestReadmeBadge:
    """Validate README badge update."""

    def setup_method(self) -> None:
        readme_path = ROOT / "README.md"
        self.content = readme_path.read_text()

    def test_badge_shows_1357_tests(self) -> None:
        assert "tests-1357_passing" in self.content


class TestRequirementsDev:
    """Validate ruff is in dev requirements."""

    def test_ruff_in_requirements_dev(self) -> None:
        req_path = ROOT / "backend" / "requirements-dev.txt"
        content = req_path.read_text()
        assert "ruff" in content
