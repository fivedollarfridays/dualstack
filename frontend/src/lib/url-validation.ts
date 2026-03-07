const ALLOWED_REDIRECT_HOSTS = new Set([
  'checkout.stripe.com',
  'billing.stripe.com',
]);

export function isAllowedRedirectUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:') return false;
    if (parsed.username || parsed.password) return false;
    return ALLOWED_REDIRECT_HOSTS.has(parsed.hostname);
  } catch {
    return false;
  }
}
