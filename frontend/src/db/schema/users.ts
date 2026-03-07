import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';

// Frontend-only table. The backend does not have a users model yet.
// When you add a users table to the backend, align this schema with it.
export const users = sqliteTable('users', {
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),
  clerkId: text('clerk_id').notNull().unique(),
  email: text('email').notNull(),
  displayName: text('display_name'),

  // Credits and subscription
  credits: integer('credits').notNull().default(0),
  subscriptionTier: text('subscription_tier', {
    enum: ['free', 'basic', 'premium', 'ultimate'],
  }).notNull().default('free'),

  // Timestamps
  createdAt: integer('created_at', { mode: 'timestamp' })
    .notNull()
    .default(sql`(unixepoch())`),
  updatedAt: integer('updated_at', { mode: 'timestamp' })
    .notNull()
    .default(sql`(unixepoch())`)
    .$onUpdate(() => new Date()),
});

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
