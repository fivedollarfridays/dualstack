import { buildCspHeader, generateNonce } from './csp';

/** Helper: extract a single CSP directive by name. */
function getDirective(csp: string, name: string): string | undefined {
  return csp
    .split(';')
    .map((d) => d.trim())
    .find((d) => d.startsWith(name));
}

describe('generateNonce', () => {
  it('returns a base64 string', () => {
    const nonce = generateNonce();
    expect(nonce).toMatch(/^[A-Za-z0-9+/=]+$/);
  });

  it('returns unique values on each call', () => {
    const a = generateNonce();
    const b = generateNonce();
    expect(a).not.toBe(b);
  });

  it('returns a string of expected length for 16 bytes', () => {
    const nonce = generateNonce();
    // 16 bytes base64 = 24 chars
    expect(nonce.length).toBe(24);
  });
});

describe('buildCspHeader', () => {
  it('includes nonce in script-src', () => {
    const csp = buildCspHeader('test-nonce-123');
    expect(csp).toContain("'nonce-test-nonce-123'");
    expect(csp).toContain('script-src');
  });

  it('does not contain unsafe-inline in script-src', () => {
    const csp = buildCspHeader('nonce123');
    const scriptSrc = getDirective(csp, 'script-src');
    expect(scriptSrc).not.toContain("'unsafe-inline'");
  });

  it('does not contain unsafe-eval in script-src', () => {
    const csp = buildCspHeader('nonce123');
    const scriptSrc = getDirective(csp, 'script-src');
    expect(scriptSrc).not.toContain("'unsafe-eval'");
  });

  it('includes strict-dynamic in script-src', () => {
    const csp = buildCspHeader('nonce123');
    const scriptSrc = getDirective(csp, 'script-src');
    expect(scriptSrc).toContain("'strict-dynamic'");
  });

  it('includes all required directives', () => {
    const csp = buildCspHeader('nonce123');
    expect(csp).toContain('default-src');
    expect(csp).toContain('script-src');
    expect(csp).toContain('style-src');
    expect(csp).toContain('img-src');
    expect(csp).toContain('font-src');
    expect(csp).toContain('connect-src');
    expect(csp).toContain('frame-src');
  });

  it('allows Clerk domains in connect-src', () => {
    const csp = buildCspHeader('nonce123');
    expect(csp).toContain('https://*.clerk.accounts.dev');
  });

  it('allows Stripe domains in frame-src', () => {
    const csp = buildCspHeader('nonce123');
    expect(csp).toContain('https://js.stripe.com');
  });

  it('includes nonce in style-src instead of unsafe-inline', () => {
    const csp = buildCspHeader('test-nonce-456');
    const styleSrc = getDirective(csp, 'style-src');
    expect(styleSrc).toContain("'nonce-test-nonce-456'");
    expect(styleSrc).not.toContain("'unsafe-inline'");
  });
});

describe('connect-src tightening', () => {
  const savedApiUrl = process.env.NEXT_PUBLIC_API_URL;
  const savedWsUrl = process.env.NEXT_PUBLIC_WS_URL;

  afterEach(() => {
    // Restore original env after each test
    if (savedApiUrl !== undefined) {
      process.env.NEXT_PUBLIC_API_URL = savedApiUrl;
    } else {
      delete process.env.NEXT_PUBLIC_API_URL;
    }
    if (savedWsUrl !== undefined) {
      process.env.NEXT_PUBLIC_WS_URL = savedWsUrl;
    } else {
      delete process.env.NEXT_PUBLIC_WS_URL;
    }
  });

  it('does not contain bare wss: scheme wildcard', () => {
    const csp = buildCspHeader('nonce123');
    const connectSrc = getDirective(csp, 'connect-src');
    // Bare "wss:" not followed by "//" is a scheme-only wildcard
    expect(connectSrc).not.toMatch(/\bwss:(?!\/\/)/);
  });

  it('does not contain bare ws: scheme wildcard', () => {
    const csp = buildCspHeader('nonce123');
    const connectSrc = getDirective(csp, 'connect-src');
    // Bare "ws:" not followed by "//" is a scheme-only wildcard
    expect(connectSrc).not.toMatch(/\bws:(?!\/\/)/);
  });

  it('includes backend API origin from NEXT_PUBLIC_API_URL', () => {
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com';
    process.env.NEXT_PUBLIC_WS_URL = 'wss://api.example.com/ws';
    const csp = buildCspHeader('nonce123');
    const connectSrc = getDirective(csp, 'connect-src');
    expect(connectSrc).toContain('https://api.example.com');
  });

  it('includes backend WS origin from NEXT_PUBLIC_WS_URL', () => {
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com';
    process.env.NEXT_PUBLIC_WS_URL = 'wss://api.example.com/ws';
    const csp = buildCspHeader('nonce123');
    const connectSrc = getDirective(csp, 'connect-src');
    expect(connectSrc).toContain('wss://api.example.com');
  });

  it('includes localhost wildcards in dev mode', () => {
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
    process.env.NEXT_PUBLIC_WS_URL = 'ws://localhost:8000/ws';
    const csp = buildCspHeader('nonce123');
    const connectSrc = getDirective(csp, 'connect-src');
    expect(connectSrc).toContain('ws://localhost:*');
    expect(connectSrc).toContain('http://localhost:*');
  });

  it('does not include localhost wildcards for production URLs', () => {
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com';
    process.env.NEXT_PUBLIC_WS_URL = 'wss://api.example.com/ws';
    const csp = buildCspHeader('nonce123');
    const connectSrc = getDirective(csp, 'connect-src');
    expect(connectSrc).not.toContain('localhost');
  });

  it('production CSP uses wss:// not ws:// for backend', () => {
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com';
    process.env.NEXT_PUBLIC_WS_URL = 'wss://api.example.com/ws';
    const csp = buildCspHeader('nonce123');
    const connectSrc = getDirective(csp, 'connect-src');
    expect(connectSrc).toContain('wss://api.example.com');
    expect(connectSrc).not.toMatch(/\bws:\/\/api\.example\.com/);
  });

  it('still includes Clerk domains after tightening', () => {
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com';
    process.env.NEXT_PUBLIC_WS_URL = 'wss://api.example.com/ws';
    const csp = buildCspHeader('nonce123');
    const connectSrc = getDirective(csp, 'connect-src');
    expect(connectSrc).toContain('https://*.clerk.accounts.dev');
  });

  it('still includes Stripe API after tightening', () => {
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com';
    process.env.NEXT_PUBLIC_WS_URL = 'wss://api.example.com/ws';
    const csp = buildCspHeader('nonce123');
    const connectSrc = getDirective(csp, 'connect-src');
    expect(connectSrc).toContain('https://api.stripe.com');
  });

  it('uses default localhost URLs when env vars are unset', () => {
    delete process.env.NEXT_PUBLIC_API_URL;
    delete process.env.NEXT_PUBLIC_WS_URL;
    const csp = buildCspHeader('nonce123');
    const connectSrc = getDirective(csp, 'connect-src');
    expect(connectSrc).toContain('ws://localhost:*');
    expect(connectSrc).toContain('http://localhost:*');
  });

  it('handles API URL with non-standard port in production', () => {
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com:8443';
    process.env.NEXT_PUBLIC_WS_URL = 'wss://api.example.com:8443/ws';
    const csp = buildCspHeader('nonce123');
    const connectSrc = getDirective(csp, 'connect-src');
    expect(connectSrc).toContain('https://api.example.com:8443');
    expect(connectSrc).toContain('wss://api.example.com:8443');
  });
});
