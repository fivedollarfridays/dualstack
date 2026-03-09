import { API_URL, authHeaders, handleResponse } from './shared';

export async function createCheckout(
  token: string,
  priceId: string,
  successUrl: string,
  cancelUrl: string
): Promise<string> {
  const res = await fetch(`${API_URL}/api/v1/billing/checkout`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({
      price_id: priceId,
      success_url: successUrl,
      cancel_url: cancelUrl,
    }),
  });
  const data = await handleResponse<{ url: string }>(res);
  return data.url;
}

export interface SubscriptionInfo {
  subscription_plan: string;
  subscription_status: string;
}

export async function getSubscription(token: string): Promise<SubscriptionInfo> {
  const res = await fetch(`${API_URL}/api/v1/users/me`, {
    headers: authHeaders(token),
  });
  return handleResponse<SubscriptionInfo>(res);
}
