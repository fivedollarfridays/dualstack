import { config } from 'dotenv';
import { migrate } from 'drizzle-orm/libsql/migrator';
import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';
import { validateDbEnv } from './validate-env';

// Load environment variables from .env.local
config({ path: '.env.local' });

async function runMigrations() {
  const { url, authToken } = validateDbEnv(
    process.env.TURSO_DATABASE_URL,
    process.env.TURSO_AUTH_TOKEN,
  );

  console.log('Connecting to Turso database...');

  const client = createClient({
    url,
    authToken,
  });

  const db = drizzle(client);

  console.log('Running migrations...');

  await migrate(db, { migrationsFolder: './drizzle' });

  console.log('Migrations completed successfully!');

  await client.close();
  process.exit(0);
}

runMigrations().catch((err) => {
  console.error('Migration failed:', err);
  process.exit(1);
});
