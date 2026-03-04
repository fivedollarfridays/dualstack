import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ItemCard } from './item-card';
import type { ItemResponse } from '@/lib/api/items';

const mockItem: ItemResponse = {
  id: 'item-1',
  user_id: 'user-1',
  title: 'Test Item',
  description: 'A description of the item',
  status: 'draft',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('ItemCard', () => {
  it('renders item title', () => {
    render(<ItemCard item={mockItem} onEdit={jest.fn()} onDelete={jest.fn()} />);
    expect(screen.getByText('Test Item')).toBeInTheDocument();
  });

  it('renders item description', () => {
    render(<ItemCard item={mockItem} onEdit={jest.fn()} onDelete={jest.fn()} />);
    expect(screen.getByText('A description of the item')).toBeInTheDocument();
  });

  it('renders status badge with draft style', () => {
    render(<ItemCard item={mockItem} onEdit={jest.fn()} onDelete={jest.fn()} />);
    const badge = screen.getByText('draft');
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain('gray');
  });

  it('renders status badge with active style', () => {
    const activeItem = { ...mockItem, status: 'active' as const };
    render(<ItemCard item={activeItem} onEdit={jest.fn()} onDelete={jest.fn()} />);
    const badge = screen.getByText('active');
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain('green');
  });

  it('renders status badge with archived style', () => {
    const archivedItem = { ...mockItem, status: 'archived' as const };
    render(<ItemCard item={archivedItem} onEdit={jest.fn()} onDelete={jest.fn()} />);
    const badge = screen.getByText('archived');
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain('yellow');
  });

  it('handles null description gracefully', () => {
    const noDesc = { ...mockItem, description: null };
    render(<ItemCard item={noDesc} onEdit={jest.fn()} onDelete={jest.fn()} />);
    expect(screen.getByText('Test Item')).toBeInTheDocument();
    expect(screen.queryByText('A description of the item')).not.toBeInTheDocument();
  });

  it('calls onEdit when edit button is clicked', async () => {
    const user = userEvent.setup();
    const onEdit = jest.fn();
    render(<ItemCard item={mockItem} onEdit={onEdit} onDelete={jest.fn()} />);

    await user.click(screen.getByRole('button', { name: /edit/i }));
    expect(onEdit).toHaveBeenCalledWith('item-1');
  });

  it('calls onDelete when delete button is clicked', async () => {
    const user = userEvent.setup();
    const onDelete = jest.fn();
    render(<ItemCard item={mockItem} onEdit={jest.fn()} onDelete={onDelete} />);

    await user.click(screen.getByRole('button', { name: /delete/i }));
    expect(onDelete).toHaveBeenCalledWith('item-1');
  });
});
