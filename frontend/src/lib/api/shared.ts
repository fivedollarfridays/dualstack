/**
 * Shared API utilities for frontend API clients.
 */

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function authHeaders(token: string): Record<string, string> {
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}

export async function handleResponse(response: Response): Promise<void>;
export async function handleResponse<T>(response: Response): Promise<T>;
export async function handleResponse<T>(response: Response): Promise<T | void> {
  if (!response.ok) {
    let message: string | undefined;
    try {
      const body = await response.json();
      message = body?.error?.message || (typeof body?.detail === 'string' ? body.detail : undefined);
    } catch {
      // Response body is not JSON — fall through to generic error
    }
    if (message) {
      throw new Error(message);
    }
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  if (response.status === 204) return;
  return response.json();
}
