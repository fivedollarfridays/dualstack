import { config } from 'dotenv';
import { migrate } from 'drizzle-orm/libsql/migrator';
import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';

// Load environment variables from .env.local
config({ path: '.env.local' });

async function runMigrations() {
  const url = process.env.TURSO_DATABASE_URL;
  const authToken = process.env.TURSO_AUTH_TOKEN;

  if (!url) {
    console.error('TURSO_DATABASE_URL is required');
    process.exit(1);
  }

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
