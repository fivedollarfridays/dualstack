/**
 * Tests for lib/auth-config.ts -- Auth configuration and Clerk detection
 */
import * as authConfig from './auth-config';

const { isClerkEnabled, DEV_USER_ID, DEV_TOKEN, getDevToken, isLocalDev } = authConfig;

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

  it('exports DEV_TOKEN as a non-empty random string (not the old static value)', () => {
    expect(typeof DEV_TOKEN).toBe('string');
    expect(DEV_TOKEN.length).toBeGreaterThan(0);
    expect(DEV_TOKEN).not.toBe('dev-token');
  });

  it('exports the same DEV_TOKEN across multiple accesses (session-stable)', () => {
    // Access the same module-level constant twice — should be identical
    const first = DEV_TOKEN;
    const second = DEV_TOKEN;
    expect(first).toBe(second);
  });
});

describe('isLocalDev', () => {
  it('returns true for localhost', () => {
    expect(isLocalDev('localhost')).toBe(true);
  });

  it('returns true for 127.0.0.1', () => {
    expect(isLocalDev('127.0.0.1')).toBe(true);
  });

  it('returns false for production hostname', () => {
    expect(isLocalDev('app.example.com')).toBe(false);
  });

  it('returns false for staging hostname', () => {
    expect(isLocalDev('staging.example.com')).toBe(false);
  });

  it('returns false when no hostname in production (SSR)', () => {
    const origEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'production';
    expect(isLocalDev('')).toBe(false);
    process.env.NODE_ENV = origEnv;
  });

  it('returns true when no hostname in development (SSR)', () => {
    const origEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';
    expect(isLocalDev('')).toBe(true);
    process.env.NODE_ENV = origEnv;
  });

  it('returns true when called without args in jsdom (localhost)', () => {
    expect(window.location.hostname).toBe('localhost');
    expect(isLocalDev()).toBe(true);
  });
});

describe('getDevToken', () => {
  it('returns dev token on localhost (jsdom default)', () => {
    const token = getDevToken();
    expect(typeof token).toBe('string');
    expect(token!.length).toBeGreaterThan(0);
    expect(token).not.toBe('dev-token');
    expect(token).toBe(DEV_TOKEN);
  });
});
