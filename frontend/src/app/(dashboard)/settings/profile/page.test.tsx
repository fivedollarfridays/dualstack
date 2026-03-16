/**
 * Tests for ProfilePage — toast notifications on profile save/delete.
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { toast } from 'sonner';
import ProfilePage from './page';
import * as api from '@/lib/api/profile';

jest.mock('sonner', () => ({
  toast: { success: jest.fn(), error: jest.fn() },
  Toaster: () => null,
}));

const mockGetToken = jest.fn().mockResolvedValue('mock-token');
jest.mock('@/contexts/auth-context', () => ({
  useAppAuth: () => ({
    userId: 'test-user-123',
    isLoaded: true,
    isSignedIn: true,
    getToken: mockGetToken,
  }),
}));

const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}));

jest.mock('@/lib/api/profile');
const mockApi = api as jest.Mocked<typeof api>;

const mockProfile = {
  id: 'user-1',
  clerk_user_id: 'clerk-123',
  display_name: 'Alice',
  avatar_url: null,
  role: 'member' as const,
  created_at: '2026-01-01',
  updated_at: '2026-01-01',
};

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(QueryClientProvider, { client: queryClient }, children);
  };
}

describe('ProfilePage toasts', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGetToken.mockResolvedValue('mock-token');
    mockApi.getProfile.mockResolvedValue(mockProfile);
  });

  it('shows success toast when profile is saved', async () => {
    const user = userEvent.setup();
    mockApi.updateProfile.mockResolvedValueOnce({ ...mockProfile, display_name: 'Bob' });

    render(<ProfilePage />, { wrapper: createWrapper() });

    await waitFor(() => expect(screen.getByDisplayValue('Alice')).toBeInTheDocument());

    const input = screen.getByDisplayValue('Alice');
    await user.clear(input);
    await user.type(input, 'Bob');
    await user.click(screen.getByText('Save'));

    await waitFor(() => expect(toast.success).toHaveBeenCalledWith('Profile saved'));
  });

  it('shows error toast when profile save fails', async () => {
    const user = userEvent.setup();
    mockApi.updateProfile.mockRejectedValueOnce(new Error('Network error'));

    render(<ProfilePage />, { wrapper: createWrapper() });

    await waitFor(() => expect(screen.getByDisplayValue('Alice')).toBeInTheDocument());

    await user.click(screen.getByText('Save'));

    await waitFor(() => expect(toast.error).toHaveBeenCalledWith('Failed to save profile'));
  });

  it('shows error toast when account deletion fails', async () => {
    const user = userEvent.setup();
    mockApi.deleteAccount.mockRejectedValueOnce(new Error('Server error'));

    render(<ProfilePage />, { wrapper: createWrapper() });

    await waitFor(() => expect(screen.getByDisplayValue('Alice')).toBeInTheDocument());

    // Click the delete button to open dialog
    const deleteButton = screen.getByText('Delete Account');
    await user.click(deleteButton);

    // Type the confirmation phrase and click delete
    const confirmInput = screen.getByLabelText('Confirmation phrase');
    await user.type(confirmInput, 'DELETE MY ACCOUNT');
    const confirmButton = screen.getByText('Permanently Delete');
    await user.click(confirmButton);

    await waitFor(() => expect(toast.error).toHaveBeenCalledWith('Failed to delete account'));
  });
});
