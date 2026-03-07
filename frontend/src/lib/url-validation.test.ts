/**
 * Tests for URL validation utility (AUDIT-005)
 */
import { isAllowedRedirectUrl } from './url-validation';

describe('isAllowedRedirectUrl', () => {
  it('allows checkout.stripe.com URLs', () => {
    expect(isAllowedRedirectUrl('https://checkout.stripe.com/c/pay/cs_test_123')).toBe(true);
  });

  it('allows billing.stripe.com URLs', () => {
    expect(isAllowedRedirectUrl('https://billing.stripe.com/p/session/test_123')).toBe(true);
  });

  it('rejects non-Stripe domains', () => {
    expect(isAllowedRedirectUrl('https://evil.com/steal-data')).toBe(false);
  });

  it('rejects lookalike domains', () => {
    expect(isAllowedRedirectUrl('https://checkout.stripe.com.evil.com/pay')).toBe(false);
  });

  it('rejects non-HTTPS URLs', () => {
    expect(isAllowedRedirectUrl('http://checkout.stripe.com/pay')).toBe(false);
  });

  it('rejects javascript: URLs', () => {
    expect(isAllowedRedirectUrl('javascript:alert(1)')).toBe(false);
  });

  it('rejects data: URLs', () => {
    expect(isAllowedRedirectUrl('data:text/html,<script>alert(1)</script>')).toBe(false);
  });

  it('rejects empty string', () => {
    expect(isAllowedRedirectUrl('')).toBe(false);
  });

  it('rejects malformed URLs', () => {
    expect(isAllowedRedirectUrl('not-a-url')).toBe(false);
  });

  it('rejects URLs with credentials', () => {
    expect(isAllowedRedirectUrl('https://user:pass@checkout.stripe.com/pay')).toBe(false);
  });
});
