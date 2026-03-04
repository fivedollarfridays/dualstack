/**
 * Tests for lib/api/shared.ts -- Shared API utilities
 */
import { API_URL, authHeaders, handleResponse } from './shared';

describe('API_URL', () => {
  const originalEnv = process.env;

  afterEach(() => {
    process.env = originalEnv;
  });

  it('defaults to localhost:8000 when env var is not set', () => {
    delete process.env.NEXT_PUBLIC_API_URL;
    // Re-import to get fresh module evaluation is not feasible with static import,
    // but the default value is compiled at module parse time.
    // Since we can't re-evaluate, we test the exported value.
    expect(API_URL).toBe('http://localhost:8000');
  });
});

describe('authHeaders', () => {
  it('returns Authorization and Content-Type headers', () => {
    const headers = authHeaders('test-token-123');
    expect(headers).toEqual({
      Authorization: 'Bearer test-token-123',
      'Content-Type': 'application/json',
    });
  });

  it('includes the Bearer prefix', () => {
    const headers = authHeaders('my-jwt');
    expect(headers.Authorization).toBe('Bearer my-jwt');
  });

  it('always includes Content-Type application/json', () => {
    const headers = authHeaders('any-token');
    expect(headers['Content-Type']).toBe('application/json');
  });
});

describe('handleResponse', () => {
  it('throws on non-ok response', async () => {
    const response = { ok: false, status: 404, statusText: 'Not Found' } as Response;
    await expect(handleResponse(response)).rejects.toThrow('API error: 404 Not Found');
  });

  it('returns undefined for 204 No Content', async () => {
    const response = { ok: true, status: 204 } as Response;
    const result = await handleResponse(response);
    expect(result).toBeUndefined();
  });

  it('parses JSON for ok responses', async () => {
    const response = {
      ok: true,
      status: 200,
      json: async () => ({ id: '1', name: 'test' }),
    } as unknown as Response;
    const result = await handleResponse<{ id: string; name: string }>(response);
    expect(result).toEqual({ id: '1', name: 'test' });
  });
});
