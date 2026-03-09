/**
 * Tests for admin hooks.
 */
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useAdminUsers, useUpdateUserRole, useAdminHealth, useAdminAuditLogs } from './use-admin';
import * as api from '@/lib/api/admin';

const mockGetToken = jest.fn().mockResolvedValue('mock-token');
jest.mock('@/contexts/auth-context', () => ({
  useAppAuth: () => ({
    userId: 'test-user-123',
    isLoaded: true,
    isSignedIn: true,
    getToken: mockGetToken,
  }),
}));

jest.mock('@/lib/api/admin');

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

describe('useAdminUsers', () => {
  it('fetches users list using the API', async () => {
    mockApi.listUsers.mockResolvedValueOnce({ users: [], total: 0 });

    const { result } = renderHook(() => useAdminUsers(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.listUsers).toHaveBeenCalledWith('mock-token', 1, 20, undefined);
  });

  it('passes custom page, limit, and search', async () => {
    mockApi.listUsers.mockResolvedValueOnce({ users: [], total: 0 });

    const { result } = renderHook(() => useAdminUsers(2, 10, 'test'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.listUsers).toHaveBeenCalledWith('mock-token', 2, 10, 'test');
  });
});

describe('useUpdateUserRole', () => {
  it('calls updateUserRole API', async () => {
    const mockUser: api.AdminUser = {
      id: 'u1',
      clerk_user_id: 'clerk-1',
      role: 'admin',
      subscription_plan: null,
      subscription_status: null,
      created_at: '2026-01-01',
      updated_at: '2026-01-01',
    };
    mockApi.updateUserRole.mockResolvedValueOnce(mockUser);

    const wrapper = createWrapper();
    const { result } = renderHook(() => useUpdateUserRole(), { wrapper });

    result.current.mutate({ userId: 'u1', role: 'admin' });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.updateUserRole).toHaveBeenCalledWith('mock-token', 'u1', 'admin');
  });
});

describe('useAdminHealth', () => {
  it('fetches health using the API', async () => {
    mockApi.getHealth.mockResolvedValueOnce({ status: 'healthy', database: 'connected', user_count: 5 });

    const { result } = renderHook(() => useAdminHealth(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.getHealth).toHaveBeenCalledWith('mock-token');
    expect(result.current.data).toEqual({ status: 'healthy', database: 'connected', user_count: 5 });
  });
});

describe('useAdminAuditLogs', () => {
  it('fetches audit logs using the API', async () => {
    mockApi.listAuditLogs.mockResolvedValueOnce({ entries: [], total: 0 });

    const { result } = renderHook(() => useAdminAuditLogs(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockApi.listAuditLogs).toHaveBeenCalledWith('mock-token', 1, 50);
  });
});

describe('null token handling', () => {
  beforeEach(() => {
    mockGetToken.mockResolvedValue(null);
  });

  afterEach(() => {
    mockGetToken.mockResolvedValue('mock-token');
  });

  it('useAdminUsers throws when token is null', async () => {
    const { result } = renderHook(() => useAdminUsers(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toEqual(new Error('Authentication required'));
  });

  it('useUpdateUserRole throws when token is null', async () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useUpdateUserRole(), { wrapper });

    result.current.mutate({ userId: 'u1', role: 'admin' });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toEqual(new Error('Authentication required'));
  });

  it('useAdminHealth throws when token is null', async () => {
    const { result } = renderHook(() => useAdminHealth(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toEqual(new Error('Authentication required'));
  });

  it('useAdminAuditLogs throws when token is null', async () => {
    const { result } = renderHook(() => useAdminAuditLogs(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toEqual(new Error('Authentication required'));
  });
});
