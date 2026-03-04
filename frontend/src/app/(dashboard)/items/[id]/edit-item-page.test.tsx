import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
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

jest.mock('@/lib/api/items', () => ({
  getItem: (...args: unknown[]) => mockGetItem(...args),
}));

jest.mock('@clerk/nextjs', () => ({
  useAuth: () => ({
    userId: 'test-user-123',
    isLoaded: true,
    isSignedIn: true,
    getToken: jest.fn().mockResolvedValue('mock-token'),
  }),
  useUser: () => ({ user: { id: 'test-user-123' }, isLoaded: true, isSignedIn: true }),
  useClerk: () => ({ signOut: jest.fn() }),
  ClerkProvider: ({ children }: { children: React.ReactNode }) => children,
  SignedIn: ({ children }: { children: React.ReactNode }) => children,
  SignedOut: () => null,
  UserButton: () => null,
}));

jest.mock('@/hooks/use-items', () => ({
  useUpdateItem: () => ({
    mutateAsync: mockUpdateMutateAsync,
    isPending: false,
  }),
  useDeleteItem: () => ({
    mutate: mockDeleteMutate,
    isPending: false,
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
});
