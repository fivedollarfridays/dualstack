"""Tests for root Makefile dev workflow targets.

Validates that the Makefile exists with required targets and correct structure.
"""

import re
from functools import cache
from pathlib import Path

PROJ_DIR = Path(__file__).resolve().parents[3]
MAKEFILE = PROJ_DIR / "Makefile"
README = PROJ_DIR / "README.md"


@cache
def _read_makefile() -> str:
    return MAKEFILE.read_text()


@cache
def _read_readme() -> str:
    return README.read_text()


class TestMakefileExists:
    def test_makefile_exists(self) -> None:
        assert MAKEFILE.is_file()

    def test_uses_tabs_not_spaces(self) -> None:
        """Makefile recipes must use tabs for indentation."""
        content = _read_makefile()
        # Find recipe lines (lines after a target that are indented)
        # They must start with a tab, not spaces
        for i, line in enumerate(content.splitlines(), 1):
            if line and line[0] == " " and not line.startswith("  #"):
                # Check if this is a recipe line (follows a target or another recipe)
                # Allow comment lines and continuation lines
                if not line.strip().startswith("#"):
                    assert False, f"Line {i} uses spaces instead of tabs: {line!r}"


class TestRequiredTargets:
    """AC: All required targets exist."""

    def test_has_setup_target(self) -> None:
        assert re.search(r"^setup:", _read_makefile(), re.MULTILINE)

    def test_has_dev_target(self) -> None:
        assert re.search(r"^dev:", _read_makefile(), re.MULTILINE)

    def test_has_test_target(self) -> None:
        assert re.search(r"^test:", _read_makefile(), re.MULTILINE)

    def test_has_build_target(self) -> None:
        assert re.search(r"^build:", _read_makefile(), re.MULTILINE)

    def test_has_clean_target(self) -> None:
        assert re.search(r"^clean:", _read_makefile(), re.MULTILINE)

    def test_has_help_target(self) -> None:
        assert re.search(r"^help:", _read_makefile(), re.MULTILINE)

    def test_help_is_default_target(self) -> None:
        """AC: `make` with no args shows help."""
        content = _read_makefile()
        # .DEFAULT_GOAL or help must be the first target
        has_default_goal = ".DEFAULT_GOAL" in content and "help" in content
        first_target = re.search(r"^(\w+):", content, re.MULTILINE)
        first_is_help = first_target and first_target.group(1) == "help"
        assert has_default_goal or first_is_help

    def test_phony_declared(self) -> None:
        content = _read_makefile()
        assert ".PHONY" in content


class TestSetupTarget:
    """AC: setup installs deps and creates .env files without overwriting."""

    def test_installs_backend_deps(self) -> None:
        content = _read_makefile()
        assert re.search(r"pip install.*requirements", content)

    def test_installs_frontend_deps(self) -> None:
        content = _read_makefile()
        assert re.search(r"npm (ci|install)", content)

    def test_copies_env_files_without_overwrite(self) -> None:
        """Must not overwrite existing .env files."""
        content = _read_makefile()
        # Should use cp -n, test -f, or [ ! -f ] to avoid overwriting
        assert re.search(r"cp -n|test -f|\[ [!] -f|if \[", content)


class TestDevTarget:
    """AC: dev starts backend, frontend, and monitoring."""

    def test_starts_backend(self) -> None:
        content = _read_makefile()
        assert re.search(r"uvicorn|python.*app", content)

    def test_starts_frontend(self) -> None:
        content = _read_makefile()
        assert re.search(r"pnpm dev", content)

    def test_starts_monitoring(self) -> None:
        content = _read_makefile()
        assert re.search(r"docker.compose", content)


class TestTestTarget:
    """AC: test runs backend and frontend suites."""

    def test_runs_pytest(self) -> None:
        content = _read_makefile()
        assert "pytest" in content

    def test_runs_frontend_tests(self) -> None:
        content = _read_makefile()
        assert re.search(r"npm (run )?test", content)


class TestReadmeUpdated:
    """AC: README quickstart references Makefile targets."""

    def test_readme_mentions_make(self) -> None:
        content = _read_readme()
        assert re.search(r"make (setup|dev|test)", content)
