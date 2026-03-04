const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function createCheckout(
  token: string,
  priceId: string
): Promise<string> {
  const res = await fetch(`${API_URL}/api/v1/billing/checkout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ price_id: priceId }),
  });
  if (!res.ok) throw new Error('Failed to create checkout');
  const data = await res.json();
  return data.url;
}

export async function openPortal(token: string): Promise<string> {
  const res = await fetch(`${API_URL}/api/v1/billing/portal`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      return_url: window.location.origin + '/dashboard',
    }),
  });
  if (!res.ok) throw new Error('Failed to open portal');
  const data = await res.json();
  return data.url;
}
