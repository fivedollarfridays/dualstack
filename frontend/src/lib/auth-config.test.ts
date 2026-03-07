/**
 * Tests for lib/auth-config.ts -- Auth configuration and Clerk detection
 */
import { isClerkEnabled, DEV_USER_ID, DEV_TOKEN } from './auth-config';

const originalEnv = process.env;

beforeEach(() => {
  process.env = { ...originalEnv };
});

afterAll(() => {
  process.env = originalEnv;
});

describe('isClerkEnabled', () => {
  it('returns true for a valid test key', () => {
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = 'pk_test_Y2xlcmsuZXhhbXBsZS5jb20k';
    expect(isClerkEnabled()).toBe(true);
  });

  it('returns true for a valid live key', () => {
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = 'pk_live_Y2xlcmsuZXhhbXBsZS5jb20k';
    expect(isClerkEnabled()).toBe(true);
  });

  it('returns false when key is undefined', () => {
    delete process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
    expect(isClerkEnabled()).toBe(false);
  });

  it('returns false for empty string', () => {
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = '';
    expect(isClerkEnabled()).toBe(false);
  });

  it('returns false for placeholder key', () => {
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = 'pk_test_placeholder';
    expect(isClerkEnabled()).toBe(false);
  });

  it('returns false for key with wrong prefix', () => {
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = 'sk_test_Y2xlcmsuZXhhbXBsZS5jb20k';
    expect(isClerkEnabled()).toBe(false);
  });

  it('returns false for key that is too short', () => {
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = 'pk_test_abc';
    expect(isClerkEnabled()).toBe(false);
  });
});

describe('constants', () => {
  it('exports DEV_USER_ID', () => {
    expect(DEV_USER_ID).toBe('dev-user-001');
  });

  it('exports DEV_TOKEN', () => {
    expect(DEV_TOKEN).toBe('dev-token');
  });
});
