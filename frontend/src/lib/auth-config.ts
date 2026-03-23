/**
 * Auth configuration: detects whether Clerk is available.
 * When Clerk keys are missing/invalid, the app uses dev-mode stubs.
 */

export const DEV_USER_ID = 'dev-user-001';
export const DEV_TOKEN = crypto.randomUUID();

/** Hostnames where dev tokens are permitted. */
const DEV_HOSTNAMES = ['localhost', '127.0.0.1'];

/**
 * Returns true if the given hostname (or current hostname) is a dev host.
 * Defaults to window.location.hostname; returns true during SSR.
 */
export function isLocalDev(hostname?: string): boolean {
  const host =
    hostname ?? (typeof window !== 'undefined' ? window.location.hostname : '');
  if (!host) return process.env.NODE_ENV === 'development'; // SSR — check env
  return DEV_HOSTNAMES.includes(host);
}

/**
 * Returns the dev token only when running on localhost or 127.0.0.1.
 * Returns null in production to prevent dev credentials from leaking.
 */
export function getDevToken(): string | null {
  return isLocalDev() ? DEV_TOKEN : null;
}

/**
 * Returns true if a valid Clerk publishable key is configured.
 * Valid keys match: pk_(test|live)_ followed by 20+ alphanumeric chars.
 */
export function isClerkEnabled(): boolean {
  const key = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  if (!key) return false;
  return /^pk_(test|live)_[A-Za-z0-9]{20,}$/.test(key);
}
