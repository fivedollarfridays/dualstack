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

// TODO: Add openPortal() function once you have a user->customer mapping.
// See backend/app/billing/service.py for the portal endpoint.
