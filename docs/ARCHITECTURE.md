# Architecture Notes

## Data Flow: Single Source of Truth

DualStack uses a **backend-first** data architecture:

- **All writes** go through the FastAPI backend (`/api/v1/*` endpoints)
- The backend owns validation, authorization, and persistence
- The frontend calls the backend API for all CRUD operations

### Frontend Database Layer (`frontend/src/db/`)

The frontend includes a direct database connection via Drizzle ORM + libsql.
This layer exists for **server-side reads only** (e.g., Next.js Server Components
or SSR data fetching). It must NOT be used for writes.

**Why this matters:**

- Using the frontend DB layer for writes would bypass backend validation,
  authorization checks, and audit logging
- Two write paths create consistency risks and make it harder to reason about
  data flow
- The backend is the authoritative source for business logic

**Guidance:**

| Operation | Use |
|-----------|-----|
| Read (SSR/Server Component) | `frontend/src/db/` is acceptable |
| Read (client-side) | Backend API via `fetch` / React Query |
| Write (any) | Backend API only |

### Recommended Future Action

If the frontend DB layer is not actively used for SSR reads, consider removing
`frontend/src/db/` entirely to eliminate the dual write path risk. If it is
needed, add a lint rule or runtime guard to prevent write operations.
