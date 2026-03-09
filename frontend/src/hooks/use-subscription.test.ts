import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useSubscription } from './use-subscription';
import * as billing from '@/lib/api/billing';

const mockGetToken = jest.fn().mockResolvedValue('mock-token');
jest.mock('@/contexts/auth-context', () => ({
  useAppAuth: () => ({
    userId: 'test-user-123',
    isLoaded: true,
    isSignedIn: true,
    getToken: mockGetToken,
  }),
}));

jest.mock('@/lib/api/billing');
const mockBilling = billing as jest.Mocked<typeof billing>;

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
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

describe('useSubscription', () => {
  it('returns subscription data on successful fetch', async () => {
    mockBilling.getSubscription.mockResolvedValueOnce({
      subscription_plan: 'pro',
      subscription_status: 'active',
    });

    const { result } = renderHook(() => useSubscription(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.plan).toBe('pro');
    expect(result.current.status).toBe('active');
    expect(mockBilling.getSubscription).toHaveBeenCalledWith('mock-token');
  });

  it('returns free defaults on API error', async () => {
    mockBilling.getSubscription.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useSubscription(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.plan).toBe('free');
    expect(result.current.status).toBe('none');
  });

  it('shows loading state while fetching', () => {
    mockBilling.getSubscription.mockReturnValue(new Promise(() => {}));

    const { result } = renderHook(() => useSubscription(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.plan).toBe('free');
    expect(result.current.status).toBe('none');
  });

  it('throws when token is null', async () => {
    mockGetToken.mockResolvedValueOnce(null);

    const { result } = renderHook(() => useSubscription(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    // With null token, the query fails and defaults apply
    expect(result.current.plan).toBe('free');
    expect(result.current.status).toBe('none');
  });
});
