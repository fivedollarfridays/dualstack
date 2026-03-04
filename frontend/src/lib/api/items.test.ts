import { listItems, createItem, getItem, updateItem, deleteItem } from './items';

// Mock global fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

const TEST_TOKEN = 'test-bearer-token';
const API_URL = 'http://localhost:8000';

beforeEach(() => {
  mockFetch.mockReset();
});

describe('listItems', () => {
  it('calls GET /api/v1/items with auth header and pagination', async () => {
    const responseData = { items: [], total: 0 };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => responseData,
    });

    const result = await listItems(TEST_TOKEN);

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_URL}/api/v1/items?page=1&limit=20`,
      {
        headers: {
          Authorization: `Bearer ${TEST_TOKEN}`,
          'Content-Type': 'application/json',
        },
      }
    );
    expect(result).toEqual(responseData);
  });

  it('passes custom page and limit params', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ items: [], total: 0 }),
    });

    await listItems(TEST_TOKEN, 3, 50);

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_URL}/api/v1/items?page=3&limit=50`,
      expect.objectContaining({})
    );
  });

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      statusText: 'Unauthorized',
    });

    await expect(listItems(TEST_TOKEN)).rejects.toThrow('API error: 401 Unauthorized');
  });
});

describe('createItem', () => {
  it('calls POST /api/v1/items with body and auth', async () => {
    const newItem = { title: 'Test Item', description: 'A test' };
    const responseData = {
      id: 'item-1',
      user_id: 'user-1',
      title: 'Test Item',
      description: 'A test',
      status: 'draft',
      created_at: '2026-01-01',
      updated_at: '2026-01-01',
    };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => responseData,
    });

    const result = await createItem(TEST_TOKEN, newItem);

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_URL}/api/v1/items`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${TEST_TOKEN}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newItem),
      }
    );
    expect(result).toEqual(responseData);
  });

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
    });

    await expect(createItem(TEST_TOKEN, { title: '' })).rejects.toThrow(
      'API error: 400 Bad Request'
    );
  });
});

describe('getItem', () => {
  it('calls GET /api/v1/items/:id with auth', async () => {
    const responseData = {
      id: 'item-1',
      user_id: 'user-1',
      title: 'Test',
      description: null,
      status: 'draft',
      created_at: '2026-01-01',
      updated_at: '2026-01-01',
    };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => responseData,
    });

    const result = await getItem(TEST_TOKEN, 'item-1');

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_URL}/api/v1/items/item-1`,
      {
        headers: {
          Authorization: `Bearer ${TEST_TOKEN}`,
          'Content-Type': 'application/json',
        },
      }
    );
    expect(result).toEqual(responseData);
  });

  it('throws on 404', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
    });

    await expect(getItem(TEST_TOKEN, 'missing')).rejects.toThrow(
      'API error: 404 Not Found'
    );
  });
});

describe('updateItem', () => {
  it('calls PATCH /api/v1/items/:id with body and auth', async () => {
    const updateData = { title: 'Updated Title' };
    const responseData = {
      id: 'item-1',
      user_id: 'user-1',
      title: 'Updated Title',
      description: null,
      status: 'draft',
      created_at: '2026-01-01',
      updated_at: '2026-01-02',
    };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => responseData,
    });

    const result = await updateItem(TEST_TOKEN, 'item-1', updateData);

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_URL}/api/v1/items/item-1`,
      {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${TEST_TOKEN}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      }
    );
    expect(result).toEqual(responseData);
  });

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    });

    await expect(
      updateItem(TEST_TOKEN, 'item-1', { title: 'X' })
    ).rejects.toThrow('API error: 500 Internal Server Error');
  });
});

describe('deleteItem', () => {
  it('calls DELETE /api/v1/items/:id with auth', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, status: 204 });

    await deleteItem(TEST_TOKEN, 'item-1');

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_URL}/api/v1/items/item-1`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${TEST_TOKEN}`,
          'Content-Type': 'application/json',
        },
      }
    );
  });

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 403,
      statusText: 'Forbidden',
    });

    await expect(deleteItem(TEST_TOKEN, 'item-1')).rejects.toThrow(
      'API error: 403 Forbidden'
    );
  });
});
