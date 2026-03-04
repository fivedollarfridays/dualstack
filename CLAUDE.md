# Claude Code Instructions

## Project Overview

DualStack is a FastAPI + Next.js SaaS starter kit. Two-stack architecture:
- `backend/` -- Python FastAPI API
- `frontend/` -- Next.js TypeScript app

## Development Workflow

### TDD Required

1. Write failing tests FIRST
2. Write minimal code to pass
3. Refactor while keeping tests green

### Coverage Gates

- Backend: 99% (pytest --cov-fail-under=99)
- Frontend: 99% (jest --coverage)

### Testing Commands

```bash
# Backend
cd backend && pytest tests/ -v
cd backend && pytest --cov=app --cov-report=term-missing tests/

# Frontend
cd frontend && npm test
cd frontend && npm run test:coverage
```

### Build Commands

```bash
# Backend
cd backend && python -c "from app.main import app"

# Frontend
cd frontend && npm run build
```

## Architecture

### Backend Patterns

- **Config**: Pydantic Settings with @lru_cache singleton
- **Database**: SQLAlchemy 2.0 async with Turso/SQLite
- **Routes**: FastAPI APIRouter, grouped by feature
- **Services**: Pure functions, not classes
- **Auth**: X-User-ID header (Clerk JWT validated upstream)
- **Errors**: Custom exception hierarchy (AppError base)

### Frontend Patterns

- **Auth**: Clerk (@clerk/nextjs)
- **Data**: React Query for server state
- **State**: Zustand for client state
- **DB**: Drizzle ORM + Turso
- **UI**: shadcn/ui + Tailwind CSS
- **API**: Feature-organized typed clients in src/lib/api/

## Key Files

| File | Purpose |
|------|---------|
| backend/app/main.py | FastAPI app entry |
| backend/app/core/config.py | Configuration |
| backend/app/core/database.py | DB connection |
| backend/app/items/ | Example CRUD entity |
| frontend/src/app/layout.tsx | Root layout |
| frontend/src/components/providers.tsx | Provider stack |
| frontend/src/db/schema/ | Drizzle schemas |
| frontend/src/lib/api/ | API clients |

## Coding Standards

- Python: type hints on all public functions
- TypeScript: strict mode enabled
- Files under 300 lines (warning at 200)
- Functions under 40 lines
- Max 12 functions per file
- TDD workflow: tests first, always
