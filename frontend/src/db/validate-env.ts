/**
 * Validate database environment variables.
 * Local file URLs (file:*) do not require an auth token.
 * Remote URLs require a non-empty auth token.
 */
export function validateDbEnv(
  url: string | undefined,
  token: string | undefined
): { url: string; authToken: string } {
  if (!url) {
    throw new Error('TURSO_DATABASE_URL environment variable is required');
  }

  const isLocalFile = url.startsWith('file:');

  if (!isLocalFile && !token) {
    throw new Error(
      'TURSO_AUTH_TOKEN is required for remote database URLs. ' +
        'Use a read-only scoped token for the frontend. ' +
        'See docs/ARCHITECTURE.md for guidance.'
    );
  }

  return { url, authToken: token || '' };
}
