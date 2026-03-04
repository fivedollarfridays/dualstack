import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useItems, useCreateItem, useUpdateItem, useDeleteItem } from './use-items';
import * as api from '@/lib/api/items';

// Override the useAuth mock from jest.setup to include getToken
const mockGetToken = jest.fn().mockResolvedValue('mock-token');
jest.mock('@clerk/nextjs', () => ({
  useAuth: () => ({
    userId: 'test-user-123',
    isLoaded: true,
    isSignedIn: true,
    getToken: mockGetToken,
  }),
  useUser: () => ({ user: { id: 'test-user-123' }, isLoaded: true, isSignedIn: true }),
  useClerk: () => ({ signOut: jest.fn() }),
  ClerkProvider: ({ children }: { children: React.ReactNode }) => children,
  SignedIn: ({ children }: { children: React.ReactNode }) => children,
  SignedOut: () => null,
  UserButton: () => null,
}));

jest.mock('@/lib/api/items');

const mockApi = api as jest.Mocked<typeof api>;

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(
      QueryClientProvider,
      { client: queryClient },
      children
    );
  };
}

const mockItem: api.ItemResponse = {
  id: 'item-1',
  user_id: 'user-1',
  title: 'Test Item',
  description: 'A test item',
  status: 'draft',
  created_at: '2026-01-01',
  updated_at: '2026-01-01',
};

describe('useItems', () => {
  it('fetches items list using the API', async () => {
    mockApi.listItems.mockResolvedValueOnce({ items: [mockItem], total: 1 });

    const { result } = renderHook(() => useItems(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.listItems).toHaveBeenCalledWith('mock-token', 1, 20);
    expect(result.current.data).toEqual({ items: [mockItem], total: 1 });
  });

  it('passes custom page and limit', async () => {
    mockApi.listItems.mockResolvedValueOnce({ items: [], total: 0 });

    const { result } = renderHook(() => useItems(2, 10), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.listItems).toHaveBeenCalledWith('mock-token', 2, 10);
  });
});

describe('useCreateItem', () => {
  it('calls createItem API and invalidates items query', async () => {
    mockApi.createItem.mockResolvedValueOnce(mockItem);

    const wrapper = createWrapper();
    const { result } = renderHook(() => useCreateItem(), { wrapper });

    result.current.mutate({ title: 'New Item', description: 'Desc' });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.createItem).toHaveBeenCalledWith('mock-token', {
      title: 'New Item',
      description: 'Desc',
    });
  });
});

describe('useUpdateItem', () => {
  it('calls updateItem API and invalidates items query', async () => {
    const updated = { ...mockItem, title: 'Updated' };
    mockApi.updateItem.mockResolvedValueOnce(updated);

    const wrapper = createWrapper();
    const { result } = renderHook(() => useUpdateItem(), { wrapper });

    result.current.mutate({ id: 'item-1', data: { title: 'Updated' } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.updateItem).toHaveBeenCalledWith('mock-token', 'item-1', {
      title: 'Updated',
    });
  });
});

describe('useDeleteItem', () => {
  it('calls deleteItem API and invalidates items query', async () => {
    mockApi.deleteItem.mockResolvedValueOnce(undefined);

    const wrapper = createWrapper();
    const { result } = renderHook(() => useDeleteItem(), { wrapper });

    result.current.mutate('item-1');

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.deleteItem).toHaveBeenCalledWith('mock-token', 'item-1');
  });
});
