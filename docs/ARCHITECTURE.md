# Architecture Notes

## Database Decision (T12.1)

The backend uses **SQLAlchemy 2.0 async** with environment-specific drivers:

| Environment | URL Source | Driver | Notes |
|-------------|-----------|--------|-------|
| Development | `TURSO_DATABASE_URL=file:local.db` | `aiosqlite` | Local SQLite file |
| Testing | (none set) | `aiosqlite` | In-memory SQLite |
| Production | `DATABASE_URL=postgresql+asyncpg://...` | `asyncpg` | PostgreSQL recommended |
| Alembic | Auto-detected | `libsql` or sync | Sync migrations via `sqlalchemy-libsql` |

**Why not remote Turso for the async runtime?**

The `sqlalchemy-libsql` dialect is sync-only — it cannot be used with
`create_async_engine`. Since all FastAPI route handlers use `async`/`await`
with SQLAlchemy `AsyncSession`, the runtime engine must use an async driver.
PostgreSQL via `asyncpg` is the standard production path for async FastAPI apps.

Turso remains the development database (local SQLite via `file:` URLs) and
Alembic can run sync migrations against remote Turso using `sqlalchemy-libsql`
when needed (e.g., `alembic upgrade head` with `TURSO_DATABASE_URL=libsql://...`).

**Configuration priority:** `DATABASE_URL` > `TURSO_DATABASE_URL` > in-memory default.

---

## Data Flow: Single Source of Truth

DualStack uses a **backend-first** data architecture:

- **All writes** go through the FastAPI backend (`/api/v1/*` endpoints)
- The backend owns validation, authorization, and persistence
- The frontend calls the backend API for all CRUD operations

### Frontend Database Layer — Removed (T12.2)

The frontend previously included a Drizzle ORM + libsql layer at
`frontend/src/db/`. An audit found **zero imports** from this directory anywhere
in the frontend codebase — no page, component, or API route used it. The layer
was removed to eliminate:

- **Dual-write risk**: Two ORM layers could write to the same database
- **Schema sync burden**: Schema definitions maintained in two places
- **Unused dependencies**: `drizzle-orm`, `drizzle-kit`, `@libsql/client`, `dotenv`, `tsx`

All data access goes through the FastAPI backend API. Frontend components use
React Query + `fetch` for client-side reads and mutations.

### Migration System — Alembic Only (T12.3)

**Alembic** (`backend/alembic/`) is the sole migration system. Drizzle Kit
migrations were removed along with the frontend DB layer. All schema changes
are managed through Alembic autogenerate against SQLAlchemy models.

```bash
# Run migrations
cd backend && alembic upgrade head

# Create a new migration
cd backend && alembic revision --autogenerate -m "description"

# Downgrade one step
cd backend && alembic downgrade -1

# Seed sample data (idempotent — safe to re-run)
cd backend && python -m scripts.seed
```
