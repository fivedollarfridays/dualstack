import React from 'react';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import EditItemPage from './page';

const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
  useParams: () => ({ id: 'item-1' }),
}));

const mockGetItem = jest.fn();
const mockUpdateMutateAsync = jest.fn();
const mockDeleteMutate = jest.fn();
const mockDeleteMutateAsync = jest.fn();
let mockUpdateError: Error | null = null;
let mockDeleteError: Error | null = null;

jest.mock('@/lib/api/items', () => ({
  getItem: (...args: unknown[]) => mockGetItem(...args),
}));

jest.mock('@/contexts/auth-context', () => ({
  useAppAuth: () => ({
    userId: 'test-user-123',
    isLoaded: true,
    isSignedIn: true,
    getToken: jest.fn().mockResolvedValue('mock-token'),
  }),
}));

jest.mock('@/hooks/use-items', () => ({
  useUpdateItem: () => ({
    mutateAsync: mockUpdateMutateAsync,
    isPending: false,
    error: mockUpdateError,
  }),
  useDeleteItem: () => ({
    mutate: mockDeleteMutate,
    mutateAsync: mockDeleteMutateAsync,
    isPending: false,
    error: mockDeleteError,
  }),
}));

// Mock react-query useQuery for the page's item fetch
jest.mock('@tanstack/react-query', () => ({
  ...jest.requireActual('@tanstack/react-query'),
  useQuery: jest.fn(),
}));

import { useQuery } from '@tanstack/react-query';
const mockUseQuery = useQuery as jest.MockedFunction<typeof useQuery>;

beforeEach(() => {
  jest.clearAllMocks();
});

const mockItem = {
  id: 'item-1',
  user_id: 'user-1',
  title: 'Existing Item',
  description: 'Existing description',
  status: 'active' as const,
  created_at: '2026-01-01',
  updated_at: '2026-01-01',
};

describe('EditItemPage', () => {
  it('renders loading state while fetching', () => {
    mockUseQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('renders error state on fetch failure', () => {
    mockUseQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Not found'),
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });

  it('renders form with item data when loaded', () => {
    mockUseQuery.mockReturnValue({
      data: mockItem,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    expect(screen.getByLabelText(/title/i)).toHaveValue('Existing Item');
    expect(screen.getByLabelText(/description/i)).toHaveValue('Existing description');
    expect(screen.getByLabelText(/status/i)).toHaveValue('active');
  });

  it('shows Update button when editing', () => {
    mockUseQuery.mockReturnValue({
      data: mockItem,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    expect(screen.getByRole('button', { name: /update/i })).toBeInTheDocument();
  });

  it('renders delete button', () => {
    mockUseQuery.mockReturnValue({
      data: mockItem,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument();
  });

  it('calls update and navigates on form submit', async () => {
    const user = userEvent.setup();
    mockUseQuery.mockReturnValue({
      data: mockItem,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);
    mockUpdateMutateAsync.mockResolvedValueOnce(mockItem);

    render(<EditItemPage />);

    // Clear and type new title
    const titleInput = screen.getByLabelText(/title/i);
    await user.clear(titleInput);
    await user.type(titleInput, 'Updated Title');
    await user.click(screen.getByRole('button', { name: /update/i }));

    expect(mockUpdateMutateAsync).toHaveBeenCalledWith({
      id: 'item-1',
      data: {
        title: 'Updated Title',
        description: 'Existing description',
        status: 'active',
      },
    });
  });

  it('renders a back button that navigates to /items', async () => {
    const user = userEvent.setup();
    mockUseQuery.mockReturnValue({
      data: mockItem,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    await user.click(screen.getByRole('button', { name: /back/i }));
    expect(mockPush).toHaveBeenCalledWith('/items');
  });

  it('shows confirm dialog and deletes when confirmed', async () => {
    const user = userEvent.setup();
    mockDeleteMutateAsync.mockResolvedValueOnce(undefined);

    mockUseQuery.mockReturnValue({
      data: mockItem,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    // Click delete to open the confirm dialog
    await user.click(screen.getByRole('button', { name: /delete/i }));

    // Dialog should appear
    const dialog = screen.getByRole('dialog');

    // Confirm the deletion via dialog button
    await user.click(within(dialog).getByRole('button', { name: /delete/i }));
    expect(mockDeleteMutateAsync).toHaveBeenCalledWith('item-1');
    await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/items'));
  });

  it('does not delete when cancel is clicked in confirm dialog', async () => {
    const user = userEvent.setup();

    mockUseQuery.mockReturnValue({
      data: mockItem,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    // Click delete to open the confirm dialog
    await user.click(screen.getByRole('button', { name: /delete/i }));

    // Dialog should appear
    const dialog = screen.getByRole('dialog');

    // Cancel
    await user.click(within(dialog).getByRole('button', { name: /cancel/i }));
    expect(mockDeleteMutateAsync).not.toHaveBeenCalled();
  });

  it('passes queryFn that calls getItem with token and id', async () => {
    mockUseQuery.mockReturnValue({
      data: mockItem,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);

    mockGetItem.mockResolvedValueOnce(mockItem);

    render(<EditItemPage />);

    // Extract and invoke the queryFn to cover lines 22-24
    const queryConfig = mockUseQuery.mock.calls[0][0] as { queryFn: () => Promise<unknown> };
    const result = await queryConfig.queryFn();

    expect(mockGetItem).toHaveBeenCalledWith('mock-token', 'item-1');
    expect(result).toEqual(mockItem);
  });

  it('queryFn throws when token is null', async () => {
    const mockGetTokenNull = jest.fn().mockResolvedValue(null);

    // Temporarily override useAppAuth to return null token
    jest.mocked(jest.requireMock('@/contexts/auth-context')).useAppAuth = () => ({
      userId: 'test-user-123',
      isLoaded: true,
      isSignedIn: true,
      getToken: mockGetTokenNull,
    });

    mockUseQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Authentication required'),
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);

    const queryConfig = mockUseQuery.mock.calls[0][0] as { queryFn: () => Promise<unknown> };
    await expect(queryConfig.queryFn()).rejects.toThrow('Authentication required');

    // Restore
    jest.mocked(jest.requireMock('@/contexts/auth-context')).useAppAuth = () => ({
      userId: 'test-user-123',
      isLoaded: true,
      isSignedIn: true,
      getToken: jest.fn().mockResolvedValue('mock-token'),
    });
  });

  it('renders error state when item is null (no data)', () => {
    mockUseQuery.mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });

  it('renders form with empty description when item description is null', () => {
    const itemWithNullDesc = {
      ...mockItem,
      description: null,
    };
    mockUseQuery.mockReturnValue({
      data: itemWithNullDesc,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    expect(screen.getByLabelText(/description/i)).toHaveValue('');
  });

  it('displays error message when updateItem has an error', () => {
    mockUpdateError = new Error('Update failed');
    mockUseQuery.mockReturnValue({
      data: mockItem,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    expect(screen.getByText('Operation failed. Please try again.')).toBeInTheDocument();
    mockUpdateError = null;
  });

  it('displays error message when deleteItemMutation has an error', () => {
    mockDeleteError = new Error('Delete failed');
    mockUseQuery.mockReturnValue({
      data: mockItem,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    expect(screen.getByText('Operation failed. Please try again.')).toBeInTheDocument();
    mockDeleteError = null;
  });

  it('does not navigate when update mutation rejects', async () => {
    const user = userEvent.setup();
    mockUseQuery.mockReturnValue({
      data: mockItem,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);
    mockUpdateMutateAsync.mockRejectedValueOnce(new Error('Network error'));

    render(<EditItemPage />);
    const titleInput = screen.getByLabelText(/title/i);
    await user.clear(titleInput);
    await user.type(titleInput, 'Updated Title');
    await user.click(screen.getByRole('button', { name: /update/i }));

    expect(mockPush).not.toHaveBeenCalled();
  });

  it('does not navigate when delete mutation rejects', async () => {
    const user = userEvent.setup();
    mockDeleteMutateAsync.mockRejectedValueOnce(new Error('Network error'));

    mockUseQuery.mockReturnValue({
      data: mockItem,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useQuery>);

    render(<EditItemPage />);
    // Open dialog and confirm
    await user.click(screen.getByRole('button', { name: /delete/i }));
    const dialog = screen.getByRole('dialog');
    await user.click(within(dialog).getByRole('button', { name: /delete/i }));

    expect(mockDeleteMutateAsync).toHaveBeenCalledWith('item-1');
    expect(mockPush).not.toHaveBeenCalled();
  });
});
