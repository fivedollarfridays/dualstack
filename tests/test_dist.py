"""Tests for the dist packaging script and Makefile target."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST_SCRIPT = ROOT / "scripts" / "dist.sh"
MAKEFILE = ROOT / "Makefile"
GITIGNORE = ROOT / ".gitignore"


class TestDistScriptExists:
    def test_dist_script_exists(self) -> None:
        assert DIST_SCRIPT.is_file(), "scripts/dist.sh must exist"

    def test_dist_script_is_executable(self) -> None:
        assert DIST_SCRIPT.stat().st_mode & 0o111, "scripts/dist.sh must be executable"

    def test_dist_script_has_shebang(self) -> None:
        first_line = DIST_SCRIPT.read_text().splitlines()[0]
        assert first_line == "#!/usr/bin/env bash", "First line must be bash shebang"


class TestDistExclusions:
    """Verify that the dist script excludes sensitive/unnecessary paths."""

    def _script_content(self) -> str:
        return DIST_SCRIPT.read_text()

    def test_dist_excludes_paircoder(self) -> None:
        content = self._script_content()
        assert ".paircoder" in content, "Must exclude .paircoder/"

    def test_dist_excludes_claude(self) -> None:
        content = self._script_content()
        assert ".claude" in content, "Must exclude .claude/"

    def test_dist_excludes_git(self) -> None:
        content = self._script_content()
        assert ".git/" in content or ".git/*" in content, "Must exclude .git/"

    def test_dist_excludes_claude_md(self) -> None:
        content = self._script_content()
        assert "CLAUDE.md" in content, "Must exclude CLAUDE.md"

    def test_dist_excludes_agents_md(self) -> None:
        content = self._script_content()
        assert "AGENTS.md" in content, "Must exclude AGENTS.md"

    def test_dist_excludes_node_modules(self) -> None:
        content = self._script_content()
        assert "node_modules" in content, "Must exclude node_modules/"

    def test_dist_excludes_venv(self) -> None:
        content = self._script_content()
        assert ".venv" in content, "Must exclude .venv/"

    def test_dist_excludes_pycache(self) -> None:
        content = self._script_content()
        assert "__pycache__" in content, "Must exclude __pycache__/"

    def test_dist_excludes_env_files(self) -> None:
        content = self._script_content()
        assert ".env" in content, "Must exclude .env files"
        # Script uses specific .env, .env.local, .env.production exclusions
        # rather than a blanket .env* pattern, so .env.example is preserved
        lines = content.splitlines()
        env_excludes = [ln for ln in lines if ".env" in ln and "-x" in ln]
        assert len(env_excludes) >= 1, "Must have at least one .env exclusion"
        blanket = [ln for ln in env_excludes if '".env*"' in ln or '"*.env"' in ln]
        assert len(blanket) == 0, "Must not blanket-exclude all .env* files"

    def test_dist_excludes_db_files(self) -> None:
        content = self._script_content()
        assert "*.db" in content, "Must exclude *.db files"

    def test_dist_excludes_monitoring_data(self) -> None:
        content = self._script_content()
        assert "monitoring/grafana/data" in content, "Must exclude grafana data"
        assert "monitoring/prometheus/data" in content, "Must exclude prometheus data"

    def test_dist_excludes_coverage(self) -> None:
        content = self._script_content()
        assert "htmlcov" in content, "Must exclude htmlcov/"
        assert ".coverage" in content, "Must exclude .coverage"

    def test_dist_excludes_next(self) -> None:
        content = self._script_content()
        assert ".next" in content, "Must exclude .next/"

    def test_dist_excludes_test_artifacts(self) -> None:
        content = self._script_content()
        assert "test-results" in content, "Must exclude test-results/"
        assert "playwright-report" in content, "Must exclude playwright-report/"


class TestMakefileAndGitignore:
    def test_makefile_has_dist_target(self) -> None:
        content = MAKEFILE.read_text()
        assert "dist:" in content, "Makefile must have a dist target"

    def test_gitignore_has_dist(self) -> None:
        content = GITIGNORE.read_text()
        assert "dist/" in content, ".gitignore must list dist/"
