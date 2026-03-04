import React from 'react';
import { render, screen } from '@testing-library/react';
import { ItemList } from './item-list';
import type { ItemResponse } from '@/lib/api/items';

const mockItems: ItemResponse[] = [
  {
    id: 'item-1',
    user_id: 'user-1',
    title: 'First Item',
    description: 'First desc',
    status: 'draft',
    created_at: '2026-01-01',
    updated_at: '2026-01-01',
  },
  {
    id: 'item-2',
    user_id: 'user-1',
    title: 'Second Item',
    description: null,
    status: 'active',
    created_at: '2026-01-02',
    updated_at: '2026-01-02',
  },
];

describe('ItemList', () => {
  it('renders a list of items', () => {
    render(
      <ItemList
        items={mockItems}
        isLoading={false}
        onEdit={jest.fn()}
        onDelete={jest.fn()}
      />
    );

    expect(screen.getByText('First Item')).toBeInTheDocument();
    expect(screen.getByText('Second Item')).toBeInTheDocument();
  });

  it('renders empty state when items is empty', () => {
    render(
      <ItemList
        items={[]}
        isLoading={false}
        onEdit={jest.fn()}
        onDelete={jest.fn()}
      />
    );

    expect(screen.getByText(/no items/i)).toBeInTheDocument();
  });

  it('renders loading state', () => {
    render(
      <ItemList
        items={[]}
        isLoading={true}
        onEdit={jest.fn()}
        onDelete={jest.fn()}
      />
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('renders items instead of loading when loaded', () => {
    render(
      <ItemList
        items={mockItems}
        isLoading={false}
        onEdit={jest.fn()}
        onDelete={jest.fn()}
      />
    );

    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    expect(screen.getByText('First Item')).toBeInTheDocument();
  });
});
