import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import NewItemPage from './page';

const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}));

const mockMutateAsync = jest.fn();
jest.mock('@/hooks/use-items', () => ({
  useCreateItem: () => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  }),
}));

beforeEach(() => {
  jest.clearAllMocks();
});

describe('NewItemPage', () => {
  it('renders heading and create form', () => {
    render(<NewItemPage />);
    expect(screen.getByText(/new item/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create/i })).toBeInTheDocument();
  });

  it('submits form and navigates to /items on success', async () => {
    const user = userEvent.setup();
    mockMutateAsync.mockResolvedValueOnce({ id: 'new-item-1' });

    render(<NewItemPage />);

    await user.type(screen.getByLabelText(/title/i), 'Brand New Item');
    await user.click(screen.getByRole('button', { name: /create/i }));

    expect(mockMutateAsync).toHaveBeenCalledWith({
      title: 'Brand New Item',
      description: '',
      status: 'draft',
    });

    // Wait for navigation
    await screen.findByText(/new item/i);
    expect(mockPush).toHaveBeenCalledWith('/items');
  });

  it('renders a cancel button that navigates back', async () => {
    const user = userEvent.setup();
    render(<NewItemPage />);

    await user.click(screen.getByRole('button', { name: /cancel/i }));
    expect(mockPush).toHaveBeenCalledWith('/items');
  });
});
