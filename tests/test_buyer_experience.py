"""Smoke tests for buyer experience — validates docs, Makefile, and env examples.

These tests verify that a buyer cloning the repo can follow the setup docs
without hitting undocumented friction points.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


class TestGettingStartedAccuracy:
    """Verify GETTING_STARTED.md claims match the actual repo."""

    def test_getting_started_exists(self) -> None:
        path = ROOT / "GETTING_STARTED.md"
        assert path.is_file(), "GETTING_STARTED.md must exist"

    def test_prerequisites_mention_python_version(self) -> None:
        text = (ROOT / "GETTING_STARTED.md").read_text()
        assert "Python 3.13" in text, "Must state Python 3.13+ requirement"

    def test_prerequisites_mention_node_version(self) -> None:
        text = (ROOT / "GETTING_STARTED.md").read_text()
        assert "Node.js 18" in text, "Must state Node.js 18+ requirement"

    def test_prerequisites_mention_pnpm(self) -> None:
        text = (ROOT / "GETTING_STARTED.md").read_text()
        assert "pnpm" in text, "Must mention pnpm as a prerequisite"

    def test_external_services_documented(self) -> None:
        text = (ROOT / "GETTING_STARTED.md").read_text()
        assert "Clerk" in text, "Must document Clerk requirement"
        assert "Stripe" in text, "Must document Stripe requirement"

    def test_make_setup_documented(self) -> None:
        text = (ROOT / "GETTING_STARTED.md").read_text()
        assert "make setup" in text, "Must document make setup command"

    def test_make_dev_documented(self) -> None:
        text = (ROOT / "GETTING_STARTED.md").read_text()
        assert "make dev" in text, "Must document make dev command"


class TestMakefileConsistency:
    """Verify Makefile targets work and use correct package managers."""

    def test_makefile_exists(self) -> None:
        assert (ROOT / "Makefile").is_file()

    def test_makefile_setup_uses_pnpm(self) -> None:
        """Setup target must use pnpm, not npm, for frontend deps."""
        text = (ROOT / "Makefile").read_text()
        # Find the setup target block
        lines = text.split("\n")
        in_setup = False
        setup_lines: list[str] = []
        for line in lines:
            if line.startswith("setup:"):
                in_setup = True
                continue
            elif in_setup and line and not line[0].isspace() and not line.startswith("#"):
                break
            elif in_setup:
                setup_lines.append(line)
        setup_block = "\n".join(setup_lines)
        assert "npm ci" not in setup_block, (
            "Makefile setup must use pnpm install, not npm ci"
        )
        assert "pnpm install" in setup_block, (
            "Makefile setup must use pnpm install for frontend"
        )

    def test_makefile_dev_uses_pnpm(self) -> None:
        """Dev target must use pnpm, not npm, for frontend."""
        text = (ROOT / "Makefile").read_text()
        lines = text.split("\n")
        in_dev = False
        dev_lines: list[str] = []
        for line in lines:
            if line.startswith("dev:"):
                in_dev = True
                continue
            elif in_dev and line and not line[0].isspace() and not line.startswith("#"):
                break
            elif in_dev:
                dev_lines.append(line)
        dev_block = "\n".join(dev_lines)
        assert "npm run dev" not in dev_block, (
            "Makefile dev must use pnpm dev, not npm run dev"
        )

    def test_makefile_test_uses_pnpm(self) -> None:
        """Test target must use pnpm, not npm, for frontend."""
        text = (ROOT / "Makefile").read_text()
        lines = text.split("\n")
        in_test = False
        test_lines: list[str] = []
        for line in lines:
            if line.startswith("test:"):
                in_test = True
                continue
            elif in_test and line and not line[0].isspace() and not line.startswith("#"):
                break
            elif in_test:
                test_lines.append(line)
        # Check each line individually — "pnpm test" contains "npm test" as
        # a substring, so we must check for bare "npm" usage, not pnpm.
        for tl in test_lines:
            stripped = tl.strip()
            if "npm" in stripped and "pnpm" not in stripped:
                pytest.fail(
                    f"Makefile test target uses npm instead of pnpm: {stripped}"
                )

    def test_makefile_lint_uses_pnpm(self) -> None:
        """Lint target must use pnpm, not npm, for frontend."""
        text = (ROOT / "Makefile").read_text()
        lines = text.split("\n")
        in_lint = False
        lint_lines: list[str] = []
        for line in lines:
            if line.startswith("lint:"):
                in_lint = True
                continue
            elif in_lint and line and not line[0].isspace() and not line.startswith("#"):
                break
            elif in_lint:
                lint_lines.append(line)
        lint_block = "\n".join(lint_lines)
        assert "npm run lint" not in lint_block, (
            "Makefile lint must use pnpm lint, not npm run lint"
        )

    def test_all_phony_targets_have_recipes(self) -> None:
        """Every .PHONY target should have a corresponding recipe."""
        text = (ROOT / "Makefile").read_text()
        for line in text.split("\n"):
            if line.startswith(".PHONY:"):
                targets = line.replace(".PHONY:", "").strip().split()
                for target in targets:
                    assert f"{target}:" in text, (
                        f"PHONY target '{target}' has no recipe"
                    )

    def test_help_target_is_default(self) -> None:
        text = (ROOT / "Makefile").read_text()
        assert ".DEFAULT_GOAL := help" in text


class TestEnvExamples:
    """Verify .env.example files exist and have required variables."""

    def test_backend_env_example_exists(self) -> None:
        assert (ROOT / "backend" / ".env.example").is_file()

    def test_frontend_env_example_exists(self) -> None:
        assert (ROOT / "frontend" / ".env.example").is_file()

    def test_backend_env_example_has_required_vars(self) -> None:
        text = (ROOT / "backend" / ".env.example").read_text()
        required = [
            "ENVIRONMENT",
            "TURSO_DATABASE_URL",
            "CLERK_JWKS_URL",
            "STRIPE_SECRET_KEY",
            "STRIPE_WEBHOOK_SECRET",
            "METRICS_API_KEY",
        ]
        for var in required:
            assert var in text, f"backend/.env.example missing {var}"

    def test_frontend_env_example_has_required_vars(self) -> None:
        text = (ROOT / "frontend" / ".env.example").read_text()
        required = [
            "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
            "NEXT_PUBLIC_API_URL",
        ]
        for var in required:
            assert var in text, f"frontend/.env.example missing {var}"


class TestCriticalPaths:
    """Verify critical files and directories exist."""

    def test_alembic_migrations_exist(self) -> None:
        versions_dir = ROOT / "backend" / "alembic" / "versions"
        assert versions_dir.is_dir(), "alembic/versions/ must exist"
        migrations = list(versions_dir.glob("*.py"))
        assert len(migrations) > 0, "Must have at least one migration"

    def test_seed_script_exists(self) -> None:
        assert (ROOT / "backend" / "scripts" / "seed.py").is_file()

    def test_check_env_script_exists(self) -> None:
        assert (ROOT / "scripts" / "check_env.py").is_file()

    def test_rename_script_exists(self) -> None:
        assert (ROOT / "scripts" / "rename.py").is_file()

    def test_smoke_test_script_exists(self) -> None:
        assert (ROOT / "scripts" / "smoke_test.sh").is_file()

    def test_python_version_file_exists(self) -> None:
        """A .python-version file helps tools like pyenv pick the right version."""
        assert (ROOT / ".python-version").is_file(), (
            ".python-version file should exist for pyenv users"
        )

    def test_nvmrc_file_exists(self) -> None:
        """An .nvmrc file helps nvm users pick the right Node version."""
        assert (ROOT / ".nvmrc").is_file(), (
            ".nvmrc file should exist for nvm users"
        )

    def test_getting_started_seed_command_matches_makefile(self) -> None:
        """GETTING_STARTED.md seed instructions should match Makefile seed target."""
        gs_text = (ROOT / "GETTING_STARTED.md").read_text()
        # The GETTING_STARTED.md should reference `make seed` or the correct
        # python -m scripts.seed command, not the wrong `python scripts/seed.py`
        assert "python scripts/seed.py" not in gs_text, (
            "GETTING_STARTED.md should use 'make seed' or 'python -m scripts.seed', "
            "not 'python scripts/seed.py' (causes ImportError)"
        )



class TestEnvCleanup:
    """Verify stale env files are removed and env example is complete."""

    def test_no_env_local_in_tree(self) -> None:
        """frontend/.env.local must not exist — it contains pk_test_placeholder."""
        path = ROOT / "frontend" / ".env.local"
        assert not path.is_file(), (
            "frontend/.env.local must be deleted — pk_test_placeholder breaks Clerk auth"
        )

    def test_env_example_has_ws_url(self) -> None:
        """frontend/.env.example must include NEXT_PUBLIC_WS_URL."""
        text = (ROOT / "frontend" / ".env.example").read_text()
        assert "NEXT_PUBLIC_WS_URL" in text, (
            "frontend/.env.example must include NEXT_PUBLIC_WS_URL"
        )

    def test_env_example_stripe_has_comment(self) -> None:
        """The line before NEXT_PUBLIC_STRIPE_PRO_PRICE_ID must describe it."""
        lines = (ROOT / "frontend" / ".env.example").read_text().splitlines()
        for i, line in enumerate(lines):
            if "NEXT_PUBLIC_STRIPE_PRO_PRICE_ID" in line and not line.startswith("#"):
                assert i > 0, "Stripe price ID cannot be the first line"
                assert "Stripe" in lines[i - 1], (
                    "Line before NEXT_PUBLIC_STRIPE_PRO_PRICE_ID must contain "
                    "a descriptive comment mentioning 'Stripe'"
                )
                return
        pytest.fail("NEXT_PUBLIC_STRIPE_PRO_PRICE_ID not found in .env.example")


class TestLockfileConsistency:
    """Verify the repo uses pnpm exclusively — no npm lockfiles."""

    def test_no_npm_lockfile(self) -> None:
        """frontend/package-lock.json must not exist — we use pnpm."""
        path = ROOT / "frontend" / "package-lock.json"
        assert not path.is_file(), (
            "frontend/package-lock.json must be deleted — project uses pnpm"
        )

    def test_pnpm_lockfile_exists(self) -> None:
        """Root pnpm-lock.yaml must exist for reproducible installs."""
        path = ROOT / "pnpm-lock.yaml"
        assert path.is_file(), (
            "pnpm-lock.yaml must exist at project root"
        )
