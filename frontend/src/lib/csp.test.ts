import { buildCspHeader, generateNonce } from './csp';

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
    const scriptSrc = csp
      .split(';')
      .find((d) => d.trim().startsWith('script-src'));
    expect(scriptSrc).not.toContain("'unsafe-inline'");
  });

  it('does not contain unsafe-eval in script-src', () => {
    const csp = buildCspHeader('nonce123');
    const scriptSrc = csp
      .split(';')
      .find((d) => d.trim().startsWith('script-src'));
    expect(scriptSrc).not.toContain("'unsafe-eval'");
  });

  it('includes strict-dynamic in script-src', () => {
    const csp = buildCspHeader('nonce123');
    const scriptSrc = csp
      .split(';')
      .find((d) => d.trim().startsWith('script-src'));
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
});
