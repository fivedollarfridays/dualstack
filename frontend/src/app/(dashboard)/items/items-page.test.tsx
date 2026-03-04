import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ItemsPage from './page';

const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}));

const mockDeleteMutate = jest.fn();
jest.mock('@/hooks/use-items', () => ({
  useItems: jest.fn(),
  useDeleteItem: () => ({
    mutate: mockDeleteMutate,
    isPending: false,
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

  it('calls deleteItem.mutate when delete is confirmed', async () => {
    const user = userEvent.setup();
    jest.spyOn(window, 'confirm').mockReturnValue(true);

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
    await user.click(screen.getByRole('button', { name: /delete/i }));

    expect(window.confirm).toHaveBeenCalled();
    expect(mockDeleteMutate).toHaveBeenCalledWith('item-1');
  });

  it('does not delete when confirm is cancelled', async () => {
    const user = userEvent.setup();
    jest.spyOn(window, 'confirm').mockReturnValue(false);

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
    await user.click(screen.getByRole('button', { name: /delete/i }));

    expect(window.confirm).toHaveBeenCalled();
    expect(mockDeleteMutate).not.toHaveBeenCalled();
  });
});
