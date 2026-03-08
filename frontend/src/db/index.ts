/**
 * Server-side read-only database connection for SSR / Server Components.
 * All writes MUST go through the backend API to preserve validation,
 * authorization, and audit logging. See docs/ARCHITECTURE.md.
 */
import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';
import * as schema from './schema';

const dbUrl = process.env.TURSO_DATABASE_URL;
if (!dbUrl) {
  throw new Error('TURSO_DATABASE_URL environment variable is required');
}

const authToken = process.env.TURSO_AUTH_TOKEN;
if (!authToken) {
  throw new Error('TURSO_AUTH_TOKEN environment variable is required');
}

const client = createClient({
  url: dbUrl,
  authToken,
});

export const db = drizzle(client, { schema });

export type Database = typeof db;
