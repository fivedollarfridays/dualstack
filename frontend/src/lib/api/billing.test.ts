import { createCheckout } from './billing';

const mockFetch = jest.fn();
global.fetch = mockFetch;

const TEST_TOKEN = 'test-bearer-token';
const API_URL = 'http://localhost:8000';

beforeEach(() => {
  mockFetch.mockReset();
});

describe('createCheckout', () => {
  it('calls POST /api/v1/billing/checkout with price_id, success_url, and cancel_url', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ url: 'https://checkout.stripe.com/session_123' }),
    });

    const url = await createCheckout(
      TEST_TOKEN,
      'price_abc',
      'https://example.com/success',
      'https://example.com/cancel'
    );

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_URL}/api/v1/billing/checkout`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${TEST_TOKEN}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          price_id: 'price_abc',
          success_url: 'https://example.com/success',
          cancel_url: 'https://example.com/cancel',
        }),
      }
    );
    expect(url).toBe('https://checkout.stripe.com/session_123');
  });

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
    });

    await expect(
      createCheckout(TEST_TOKEN, 'price_abc', 'https://example.com/ok', 'https://example.com/cancel')
    ).rejects.toThrow('API error: 400 Bad Request');
  });
});
