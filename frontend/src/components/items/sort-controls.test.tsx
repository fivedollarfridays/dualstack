/**
 * Tests for SortControls component.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SortControls } from './sort-controls';

describe('SortControls', () => {
  it('renders sort field options', () => {
    render(<SortControls sortBy="created_at" sortDir="desc" onSortChange={jest.fn()} />);
    expect(screen.getByLabelText('Sort by')).toBeInTheDocument();
    expect(screen.getByText('Created')).toBeInTheDocument();
    expect(screen.getByText('Updated')).toBeInTheDocument();
    expect(screen.getByText('Title')).toBeInTheDocument();
  });

  it('calls onSortChange when field changes', async () => {
    const user = userEvent.setup();
    const onSortChange = jest.fn();
    render(<SortControls sortBy="created_at" sortDir="desc" onSortChange={onSortChange} />);

    await user.selectOptions(screen.getByLabelText('Sort by'), 'title');

    expect(onSortChange).toHaveBeenCalledWith('title', 'desc');
  });

  it('toggles direction on button click', async () => {
    const user = userEvent.setup();
    const onSortChange = jest.fn();
    render(<SortControls sortBy="created_at" sortDir="desc" onSortChange={onSortChange} />);

    await user.click(screen.getByLabelText('Sort ascending'));

    expect(onSortChange).toHaveBeenCalledWith('created_at', 'asc');
  });

  it('toggles direction from asc to desc on button click', async () => {
    const user = userEvent.setup();
    const onSortChange = jest.fn();
    render(<SortControls sortBy="created_at" sortDir="asc" onSortChange={onSortChange} />);

    await user.click(screen.getByLabelText('Sort descending'));

    expect(onSortChange).toHaveBeenCalledWith('created_at', 'desc');
  });

  it('shows ascending arrow when asc', () => {
    render(<SortControls sortBy="title" sortDir="asc" onSortChange={jest.fn()} />);
    expect(screen.getByLabelText('Sort descending')).toBeInTheDocument();
  });
});
