/**
 * Server-side read-only database connection for SSR / Server Components.
 * All writes MUST go through the backend API to preserve validation,
 * authorization, and audit logging. See docs/ARCHITECTURE.md.
 *
 * For production, use a read-only scoped Turso token for the frontend.
 */
import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';
import * as schema from './schema';
import { validateDbEnv } from './validate-env';

const { url, authToken } = validateDbEnv(
  process.env.TURSO_DATABASE_URL,
  process.env.TURSO_AUTH_TOKEN,
);

const client = createClient({ url, authToken });

export const db = drizzle(client, { schema });

export type Database = typeof db;
