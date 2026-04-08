# Contributing to DualStack

Thanks for your interest in contributing to DualStack! This guide covers everything you need to get started.

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.13+ | `python3 --version` |
| Node.js | 22+ | `node --version` |
| pnpm | 9+ | `pnpm --version` |
| Git | 2.30+ | `git --version` |

## Getting Started

1. **Fork and clone** the repository:

   ```bash
   git clone https://github.com/<your-username>/dualstack.git
   cd dualstack
   ```

2. **Run setup** (installs dependencies, creates `.env` files, runs migrations):

   ```bash
   make setup
   ```

3. **Configure environment variables** in `backend/.env` and `frontend/.env.local`. See the `.env.example` files for required values. Run `make check-env` to validate your configuration.

4. **Seed demo data** (optional):

   ```bash
   make seed
   ```

5. **Start the dev server**:

   ```bash
   make dev
   ```

   This starts the backend (port 8000), frontend (port 3000), and monitoring stack (Grafana on 3001).

## Running Tests

Run the full test suite:

```bash
make test
```

This runs both backend (pytest) and frontend (Jest) tests. All tests must pass before submitting a PR.

You can also run them separately:

```bash
# Backend only
cd backend && pytest tests/

# Frontend only
cd frontend && pnpm test
```

## Makefile Commands

The Makefile is the canonical interface for common tasks:

| Command | Description |
|---------|-------------|
| `make setup` | Install deps, create env files, run migrations |
| `make dev` | Start all services |
| `make test` | Run backend + frontend tests |
| `make lint` | Run ruff (backend) + ESLint (frontend) |
| `make format` | Format backend code with ruff |
| `make seed` | Seed demo data |
| `make smoke` | Run smoke tests against a running API |
| `make clean` | Stop services, remove build artifacts |

## Pull Request Process

1. **Fork** the repository and create a branch from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below.

3. **Write tests** for any new functionality or bug fixes.

4. **Run linting and tests** to verify everything passes:

   ```bash
   make lint
   make test
   ```

5. **Commit** with a clear message describing the change:

   ```bash
   git commit -m "feat: add widget sorting endpoint"
   ```

6. **Push** to your fork and open a pull request against `main`.

7. **In your PR description**, include:
   - What the change does and why
   - How to test it
   - Any breaking changes

## Coding Standards

### Python (Backend)

- **Linter/Formatter**: [ruff](https://docs.astral.sh/ruff/) -- run `make lint` and `make format`
- **Type hints**: Use type annotations on all function signatures
- **Async**: Use `async def` for database and I/O operations
- **Testing**: pytest with async support -- place tests in `backend/tests/`
- **Architecture constraints**:
  - Source files: < 400 lines, < 15 functions
  - Functions: < 50 lines
  - Imports: < 20 per file

### TypeScript (Frontend)

- **Linter**: ESLint -- run `cd frontend && pnpm lint`
- **Framework**: Next.js 15 App Router with React 18
- **Styling**: Tailwind CSS + shadcn/ui components
- **Testing**: Jest for unit tests, Playwright for E2E
- **Architecture constraints**: Same line/function limits as backend

### General

- No hardcoded secrets or API keys -- use environment variables
- Pre-commit hooks run automatically (ruff lint + format)
- Follow existing patterns in the codebase when adding new modules

## Project Structure

```
backend/         # FastAPI application
  app/           # Source code (models, routes, services)
  tests/         # pytest test suite
frontend/        # Next.js application
  src/           # Source code (components, hooks, pages)
  __tests__/     # Jest test suite
monitoring/      # Grafana + Prometheus + Alertmanager
scripts/         # Utility scripts (seed, env check, smoke test)
```

## Questions?

- **Bug reports and feature requests**: Open a [GitHub Issue](https://github.com/YOUR_USERNAME/dualstack/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/YOUR_USERNAME/dualstack/discussions) for questions and ideas

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
