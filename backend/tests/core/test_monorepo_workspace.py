"""Tests for monorepo workspace configuration.

Validates pnpm workspace setup, root package.json scripts,
and README documentation for cross-stack operations.
"""

import json
import re
from functools import cache
from pathlib import Path

import yaml

PROJ_DIR = Path(__file__).resolve().parents[3]
WORKSPACE_YAML = PROJ_DIR / "pnpm-workspace.yaml"
ROOT_PKG = PROJ_DIR / "package.json"
FRONTEND_PKG = PROJ_DIR / "frontend" / "package.json"
README = PROJ_DIR / "README.md"


@cache
def _load_workspace() -> dict:
    return yaml.safe_load(WORKSPACE_YAML.read_text())


@cache
def _load_root_pkg() -> dict:
    return json.loads(ROOT_PKG.read_text())


@cache
def _load_frontend_pkg() -> dict:
    return json.loads(FRONTEND_PKG.read_text())


@cache
def _read_readme() -> str:
    return README.read_text()


class TestWorkspaceConfig:
    """AC: pnpm-workspace.yaml exists and includes frontend."""

    def test_workspace_yaml_exists(self) -> None:
        assert WORKSPACE_YAML.is_file()

    def test_includes_frontend(self) -> None:
        ws = _load_workspace()
        packages = ws.get("packages", [])
        assert any("frontend" in p for p in packages)


class TestRootPackageJson:
    """AC: Root package.json exists with workspace scripts."""

    def test_root_package_json_exists(self) -> None:
        assert ROOT_PKG.is_file()

    def test_is_private(self) -> None:
        pkg = _load_root_pkg()
        assert pkg.get("private") is True

    def test_has_dev_script(self) -> None:
        pkg = _load_root_pkg()
        assert "dev" in pkg.get("scripts", {})

    def test_has_test_script(self) -> None:
        pkg = _load_root_pkg()
        assert "test" in pkg.get("scripts", {})

    def test_has_build_script(self) -> None:
        pkg = _load_root_pkg()
        assert "build" in pkg.get("scripts", {})

    def test_has_install_all_script(self) -> None:
        pkg = _load_root_pkg()
        scripts = pkg.get("scripts", {})
        assert "install:all" in scripts or "setup" in scripts


class TestFrontendPackageJson:
    """AC: Frontend package.json has a name field for workspace resolution."""

    def test_has_name_field(self) -> None:
        pkg = _load_frontend_pkg()
        assert "name" in pkg
        assert len(pkg["name"]) > 0

    def test_existing_scripts_intact(self) -> None:
        """AC: Existing npm commands in frontend continue to work."""
        pkg = _load_frontend_pkg()
        scripts = pkg.get("scripts", {})
        assert "dev" in scripts
        assert "build" in scripts
        assert "test" in scripts
        assert "lint" in scripts


class TestReadmeWorkspaceDocs:
    """AC: README documents monorepo workspace setup."""

    def test_mentions_pnpm(self) -> None:
        content = _read_readme()
        assert re.search(r"pnpm", content, re.IGNORECASE)

    def test_mentions_workspace(self) -> None:
        content = _read_readme()
        assert re.search(r"workspace|monorepo", content, re.IGNORECASE)
