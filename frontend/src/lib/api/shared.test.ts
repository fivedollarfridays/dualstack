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
  it('throws with backend error message when response body has error.message', async () => {
    const response = {
      ok: false,
      status: 422,
      statusText: 'Unprocessable Entity',
      json: async () => ({ error: { message: 'price_id is required' } }),
    } as unknown as Response;
    await expect(handleResponse(response)).rejects.toThrow('price_id is required');
  });

  it('throws with backend detail string when response body has detail', async () => {
    const response = {
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: async () => ({ detail: 'Item not found' }),
    } as unknown as Response;
    await expect(handleResponse(response)).rejects.toThrow('Item not found');
  });

  it('falls back to status text when response body parsing fails', async () => {
    const response = {
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: async () => { throw new Error('not json'); },
    } as unknown as Response;
    await expect(handleResponse(response)).rejects.toThrow('API error: 500 Internal Server Error');
  });

  it('falls back to status text when response body has no recognized error field', async () => {
    const response = {
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: async () => ({ unknown: 'field' }),
    } as unknown as Response;
    await expect(handleResponse(response)).rejects.toThrow('API error: 400 Bad Request');
  });

  it('falls back to status text when detail is an array (FastAPI validation error)', async () => {
    const response = {
      ok: false,
      status: 422,
      statusText: 'Unprocessable Entity',
      json: async () => ({ detail: [{ loc: ['body', 'price_id'], msg: 'field required', type: 'missing' }] }),
    } as unknown as Response;
    await expect(handleResponse(response)).rejects.toThrow('API error: 422 Unprocessable Entity');
  });

  it('falls back to status text when response body is null', async () => {
    const response = {
      ok: false,
      status: 502,
      statusText: 'Bad Gateway',
      json: async () => null,
    } as unknown as Response;
    await expect(handleResponse(response)).rejects.toThrow('API error: 502 Bad Gateway');
  });

  it('extracts error.message when error object exists but no detail', async () => {
    const response = {
      ok: false,
      status: 422,
      statusText: 'Unprocessable Entity',
      json: async () => ({ error: { code: 'VALIDATION', message: 'Invalid input' } }),
    } as unknown as Response;
    await expect(handleResponse(response)).rejects.toThrow('Invalid input');
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
