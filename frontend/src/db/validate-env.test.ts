import { validateDbEnv } from './validate-env';

describe('validateDbEnv', () => {
  it('throws when TURSO_DATABASE_URL is missing', () => {
    expect(() => validateDbEnv(undefined, 'token')).toThrow(
      'TURSO_DATABASE_URL environment variable is required'
    );
  });

  it('throws when TURSO_DATABASE_URL is empty', () => {
    expect(() => validateDbEnv('', 'token')).toThrow(
      'TURSO_DATABASE_URL environment variable is required'
    );
  });

  it('allows local file URL without auth token', () => {
    expect(() => validateDbEnv('file:local.db', '')).not.toThrow();
  });

  it('allows local file URL with undefined token', () => {
    expect(() => validateDbEnv('file:local.db', undefined)).not.toThrow();
  });

  it('throws when remote URL has empty auth token', () => {
    expect(() => validateDbEnv('libsql://db.turso.io', '')).toThrow(
      'TURSO_AUTH_TOKEN is required for remote database URLs'
    );
  });

  it('throws when remote URL has undefined auth token', () => {
    expect(() => validateDbEnv('https://db.turso.io', undefined)).toThrow(
      'TURSO_AUTH_TOKEN is required for remote database URLs'
    );
  });

  it('allows remote URL with valid auth token', () => {
    expect(() =>
      validateDbEnv('libsql://db.turso.io', 'eyJ...')
    ).not.toThrow();
  });

  it('returns url and token for local file URL', () => {
    const result = validateDbEnv('file:local.db', '');
    expect(result).toEqual({ url: 'file:local.db', authToken: '' });
  });

  it('returns url and token for remote URL', () => {
    const result = validateDbEnv('libsql://db.turso.io', 'my-token');
    expect(result).toEqual({
      url: 'libsql://db.turso.io',
      authToken: 'my-token',
    });
  });
});
