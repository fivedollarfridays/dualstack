import React from 'react';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ItemsPage from './page';

const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}));

const mockDeleteMutate = jest.fn();
const mockDeleteMutateAsync = jest.fn();
let mockDeleteError: Error | null = null;
jest.mock('@/hooks/use-items', () => ({
  useItems: jest.fn(),
  useDeleteItem: () => ({
    mutate: mockDeleteMutate,
    mutateAsync: mockDeleteMutateAsync,
    isPending: false,
    error: mockDeleteError,
  }),
}));

import { useItems } from '@/hooks/use-items';
const mockUseItems = useItems as jest.MockedFunction<typeof useItems>;

beforeEach(() => {
  jest.clearAllMocks();
});

describe('ItemsPage', () => {
  it('renders loading state', () => {
    mockUseItems.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as ReturnType<typeof useItems>);

    render(<ItemsPage />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('renders error state', () => {
    mockUseItems.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Network error'),
    } as ReturnType<typeof useItems>);

    render(<ItemsPage />);
    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });

  it('renders items list when data loaded', () => {
    mockUseItems.mockReturnValue({
      data: {
        items: [
          {
            id: 'item-1',
            user_id: 'user-1',
            title: 'My Item',
            description: 'Desc',
            status: 'active',
            created_at: '2026-01-01',
            updated_at: '2026-01-01',
          },
        ],
        total: 1,
      },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useItems>);

    render(<ItemsPage />);
    expect(screen.getByText('My Item')).toBeInTheDocument();
  });

  it('renders "New Item" button', () => {
    mockUseItems.mockReturnValue({
      data: { items: [], total: 0 },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useItems>);

    render(<ItemsPage />);
    expect(screen.getByRole('button', { name: /new item/i })).toBeInTheDocument();
  });

  it('navigates to /items/new when "New Item" is clicked', async () => {
    const user = userEvent.setup();
    mockUseItems.mockReturnValue({
      data: { items: [], total: 0 },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useItems>);

    render(<ItemsPage />);
    await user.click(screen.getByRole('button', { name: /new item/i }));
    expect(mockPush).toHaveBeenCalledWith('/items/new');
  });

  it('navigates to edit page when edit is clicked', async () => {
    const user = userEvent.setup();
    mockUseItems.mockReturnValue({
      data: {
        items: [
          {
            id: 'item-1',
            user_id: 'user-1',
            title: 'My Item',
            description: null,
            status: 'draft',
            created_at: '2026-01-01',
            updated_at: '2026-01-01',
          },
        ],
        total: 1,
      },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useItems>);

    render(<ItemsPage />);
    await user.click(screen.getByRole('button', { name: /edit/i }));
    expect(mockPush).toHaveBeenCalledWith('/items/item-1');
  });

  it('shows confirm dialog and deletes when confirmed', async () => {
    const user = userEvent.setup();
    mockDeleteMutateAsync.mockResolvedValueOnce(undefined);

    mockUseItems.mockReturnValue({
      data: {
        items: [
          {
            id: 'item-1',
            user_id: 'user-1',
            title: 'My Item',
            description: null,
            status: 'draft',
            created_at: '2026-01-01',
            updated_at: '2026-01-01',
          },
        ],
        total: 1,
      },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useItems>);

    render(<ItemsPage />);
    // Click delete to open the confirm dialog
    await user.click(screen.getByRole('button', { name: /delete/i }));

    // Dialog should appear
    const dialog = screen.getByRole('dialog');

    // Confirm the deletion via the dialog button
    await user.click(within(dialog).getByRole('button', { name: /delete/i }));
    expect(mockDeleteMutateAsync).toHaveBeenCalledWith('item-1');
  });

  it('does not delete when cancel is clicked in confirm dialog', async () => {
    const user = userEvent.setup();

    mockUseItems.mockReturnValue({
      data: {
        items: [
          {
            id: 'item-1',
            user_id: 'user-1',
            title: 'My Item',
            description: null,
            status: 'draft',
            created_at: '2026-01-01',
            updated_at: '2026-01-01',
          },
        ],
        total: 1,
      },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useItems>);

    render(<ItemsPage />);
    // Click delete to open the confirm dialog
    await user.click(screen.getByRole('button', { name: /delete/i }));

    // Dialog should appear
    const dialog = screen.getByRole('dialog');

    // Cancel the deletion
    await user.click(within(dialog).getByRole('button', { name: /cancel/i }));
    expect(mockDeleteMutateAsync).not.toHaveBeenCalled();
  });

  it('displays delete error message when deleteItem has an error', () => {
    mockDeleteError = new Error('Delete failed');
    mockUseItems.mockReturnValue({
      data: { items: [], total: 0 },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useItems>);

    render(<ItemsPage />);
    expect(screen.getByText('Delete failed. Please try again.')).toBeInTheDocument();
    mockDeleteError = null;
  });

  it('does not throw when delete mutation rejects', async () => {
    const user = userEvent.setup();
    mockDeleteMutateAsync.mockRejectedValueOnce(new Error('Network error'));

    mockUseItems.mockReturnValue({
      data: {
        items: [
          {
            id: 'item-1',
            user_id: 'user-1',
            title: 'My Item',
            description: null,
            status: 'draft',
            created_at: '2026-01-01',
            updated_at: '2026-01-01',
          },
        ],
        total: 1,
      },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useItems>);

    render(<ItemsPage />);
    // Open dialog and confirm
    await user.click(screen.getByRole('button', { name: /delete/i }));
    const dialog = screen.getByRole('dialog');
    await user.click(within(dialog).getByRole('button', { name: /delete/i }));

    expect(mockDeleteMutateAsync).toHaveBeenCalledWith('item-1');
  });

  describe('pagination', () => {
    it('renders Previous and Next buttons', () => {
      mockUseItems.mockReturnValue({
        data: { items: [], total: 0 },
        isLoading: false,
        error: null,
      } as ReturnType<typeof useItems>);

      render(<ItemsPage />);
      expect(screen.getByRole('button', { name: /previous/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();
    });

    it('disables Previous on first page', () => {
      mockUseItems.mockReturnValue({
        data: { items: [], total: 0 },
        isLoading: false,
        error: null,
      } as ReturnType<typeof useItems>);

      render(<ItemsPage />);
      expect(screen.getByRole('button', { name: /previous/i })).toBeDisabled();
    });

    it('disables Next when on the last page', () => {
      mockUseItems.mockReturnValue({
        data: { items: [{ id: '1', user_id: 'u', title: 'T', description: null, status: 'draft', created_at: '', updated_at: '' }], total: 1 },
        isLoading: false,
        error: null,
      } as ReturnType<typeof useItems>);

      render(<ItemsPage />);
      expect(screen.getByRole('button', { name: /next/i })).toBeDisabled();
    });

    it('shows current page number', () => {
      mockUseItems.mockReturnValue({
        data: { items: [], total: 0 },
        isLoading: false,
        error: null,
      } as ReturnType<typeof useItems>);

      render(<ItemsPage />);
      expect(screen.getByText(/page 1/i)).toBeInTheDocument();
    });

    it('enables Next when there are more pages', () => {
      // 25 items with page size 20 = 2 pages
      mockUseItems.mockReturnValue({
        data: { items: Array(20).fill({ id: '1', user_id: 'u', title: 'T', description: null, status: 'draft', created_at: '', updated_at: '' }), total: 25 },
        isLoading: false,
        error: null,
      } as ReturnType<typeof useItems>);

      render(<ItemsPage />);
      expect(screen.getByRole('button', { name: /next/i })).not.toBeDisabled();
    });

    it('advances to next page when Next is clicked', async () => {
      const user = userEvent.setup();
      mockUseItems.mockReturnValue({
        data: { items: Array(20).fill({ id: '1', user_id: 'u', title: 'T', description: null, status: 'draft', created_at: '', updated_at: '' }), total: 25 },
        isLoading: false,
        error: null,
      } as ReturnType<typeof useItems>);

      render(<ItemsPage />);
      await user.click(screen.getByRole('button', { name: /next/i }));
      expect(screen.getByText(/page 2/i)).toBeInTheDocument();
    });

    it('resets to last valid page when total shrinks below current page', async () => {
      const user = userEvent.setup();
      // Start with 2 pages worth of items
      mockUseItems.mockReturnValue({
        data: { items: Array(20).fill({ id: '1', user_id: 'u', title: 'T', description: null, status: 'draft', created_at: '', updated_at: '' }), total: 25 },
        isLoading: false,
        error: null,
      } as ReturnType<typeof useItems>);

      const { rerender } = render(<ItemsPage />);
      await user.click(screen.getByRole('button', { name: /next/i }));
      expect(screen.getByText(/page 2/i)).toBeInTheDocument();

      // Now total drops to fit on 1 page (items were deleted)
      mockUseItems.mockReturnValue({
        data: { items: [{ id: '1', user_id: 'u', title: 'T', description: null, status: 'draft', created_at: '', updated_at: '' }], total: 1 },
        isLoading: false,
        error: null,
      } as ReturnType<typeof useItems>);

      rerender(<ItemsPage />);
      expect(screen.getByText(/page 1/i)).toBeInTheDocument();
    });

    it('goes back to previous page when Previous is clicked', async () => {
      const user = userEvent.setup();
      mockUseItems.mockReturnValue({
        data: { items: Array(20).fill({ id: '1', user_id: 'u', title: 'T', description: null, status: 'draft', created_at: '', updated_at: '' }), total: 45 },
        isLoading: false,
        error: null,
      } as ReturnType<typeof useItems>);

      render(<ItemsPage />);
      // Go to page 2
      await user.click(screen.getByRole('button', { name: /next/i }));
      expect(screen.getByText(/page 2/i)).toBeInTheDocument();
      // Go back to page 1
      await user.click(screen.getByRole('button', { name: /previous/i }));
      expect(screen.getByText(/page 1/i)).toBeInTheDocument();
    });
  });
});
