/**
 * Auth configuration: detects whether Clerk is available.
 * When Clerk keys are missing/invalid, the app uses dev-mode stubs.
 */

export const DEV_USER_ID = 'dev-user-001';
export const DEV_TOKEN = 'dev-token';

/**
 * Returns true if a valid Clerk publishable key is configured.
 * Valid keys match: pk_(test|live)_ followed by 20+ alphanumeric chars.
 */
export function isClerkEnabled(): boolean {
  const key = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  if (!key) return false;
  return /^pk_(test|live)_[A-Za-z0-9]{20,}$/.test(key);
}
