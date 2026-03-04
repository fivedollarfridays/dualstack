import { createCheckout } from './billing';

const mockFetch = jest.fn();
global.fetch = mockFetch;

const TEST_TOKEN = 'test-bearer-token';
const API_URL = 'http://localhost:8000';

beforeEach(() => {
  mockFetch.mockReset();
});

describe('createCheckout', () => {
  it('calls POST /api/v1/billing/checkout and returns URL', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ url: 'https://checkout.stripe.com/session_123' }),
    });

    const url = await createCheckout(TEST_TOKEN, 'price_abc');

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_URL}/api/v1/billing/checkout`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${TEST_TOKEN}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ price_id: 'price_abc' }),
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

    await expect(createCheckout(TEST_TOKEN, 'price_abc')).rejects.toThrow(
      'API error: 400 Bad Request'
    );
  });
});
