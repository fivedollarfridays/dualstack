/**
 * Generate a cryptographically random nonce for CSP headers.
 * Uses Web Crypto API for Edge runtime compatibility.
 */
export function generateNonce(): string {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return btoa(String.fromCharCode(...bytes));
}

/**
 * Extract the origin (protocol + host + port) from a URL string.
 * Returns the origin portion only, stripping any path/query.
 */
export function extractOrigin(url: string): string {
  try {
    const parsed = new URL(url);
    return parsed.origin;
  } catch {
    return url;
  }
}

/**
 * Determine whether a URL points to localhost (development mode).
 */
function isLocalhostUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return (
      parsed.hostname === 'localhost' || parsed.hostname === '127.0.0.1'
    );
  } catch {
    return false;
  }
}

/**
 * Build the connect-src directive value with env-derived backend origins.
 *
 * - Always includes 'self', Clerk domains, and Stripe API.
 * - Adds specific backend HTTP and WS origins from NEXT_PUBLIC_API_URL
 *   and NEXT_PUBLIC_WS_URL environment variables.
 * - In dev (localhost URLs), adds ws://localhost:* and http://localhost:*
 *   wildcards for HMR and local API flexibility.
 * - Never emits bare ws: or wss: scheme-only wildcards.
 */
export function buildConnectSrc(): string {
  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const wsUrl =
    process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

  const apiOrigin = extractOrigin(apiUrl);
  const wsOrigin = extractOrigin(wsUrl);

  const isDev = isLocalhostUrl(apiUrl) || isLocalhostUrl(wsUrl);

  const sources = [
    "'self'",
    'https://*.clerk.accounts.dev',
    'https://api.stripe.com',
  ];

  if (isDev) {
    sources.push('ws://localhost:*', 'http://localhost:*');
  } else {
    sources.push(apiOrigin, wsOrigin);
  }

  return `connect-src ${sources.join(' ')}`;
}

// Static CSP parts that only vary by nonce.
const SCRIPT_SRC =
  "script-src 'self' 'nonce-${NONCE}' 'strict-dynamic' https://*.clerk.accounts.dev";
const STYLE_SRC = "style-src 'self' 'nonce-${NONCE}'";
const IMG_SRC =
  "img-src 'self' data: https://*.clerk.accounts.dev https://img.clerk.com";
const FONT_SRC = "font-src 'self'";
const FRAME_SRC =
  'frame-src https://js.stripe.com https://*.clerk.accounts.dev';
const WORKER_SRC = "worker-src 'self' blob:";
const FORM_ACTION = "form-action 'self'";
const BASE_URI = "base-uri 'none'";
const OBJECT_SRC = "object-src 'none'";

/**
 * Build a Content-Security-Policy header value with a nonce.
 * Uses 'strict-dynamic' + nonce for script-src and nonce for style-src.
 * No 'unsafe-inline' or 'unsafe-eval' allowed.
 *
 * connect-src is derived from NEXT_PUBLIC_API_URL and NEXT_PUBLIC_WS_URL
 * environment variables rather than using wildcard ws:/wss: schemes.
 */
export function buildCspHeader(nonce: string): string {
  const directives = [
    "default-src 'self'",
    SCRIPT_SRC.replace('${NONCE}', nonce),
    STYLE_SRC.replace('${NONCE}', nonce),
    IMG_SRC,
    FONT_SRC,
    buildConnectSrc(),
    FRAME_SRC,
    WORKER_SRC,
    FORM_ACTION,
    BASE_URI,
    OBJECT_SRC,
  ];
  return directives.join('; ');
}
