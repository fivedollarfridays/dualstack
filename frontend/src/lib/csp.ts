/**
 * Generate a cryptographically random nonce for CSP headers.
 * Uses Web Crypto API for Edge runtime compatibility.
 */
export function generateNonce(): string {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return btoa(String.fromCharCode(...bytes));
}

// Pre-computed static CSP parts — only the nonce changes per request.
const CSP_PREFIX = "default-src 'self'; script-src 'self' 'nonce-";
const CSP_MIDDLE = "' 'strict-dynamic' https://*.clerk.accounts.dev; style-src 'self' 'nonce-";
const CSP_SUFFIX =
  "'; " +
  "img-src 'self' data: https://*.clerk.accounts.dev https://img.clerk.com; " +
  "font-src 'self'; " +
  "connect-src 'self' https://*.clerk.accounts.dev https://api.stripe.com; " +
  "frame-src https://js.stripe.com https://*.clerk.accounts.dev; " +
  "worker-src 'self' blob:";

/**
 * Build a Content-Security-Policy header value with a nonce.
 * Uses 'strict-dynamic' + nonce for script-src and nonce for style-src.
 * No 'unsafe-inline' or 'unsafe-eval' allowed.
 */
export function buildCspHeader(nonce: string): string {
  return CSP_PREFIX + nonce + CSP_MIDDLE + nonce + CSP_SUFFIX;
}
