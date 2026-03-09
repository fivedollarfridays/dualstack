/**
 * Tests for SearchBar component.
 */
import React from 'react';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SearchBar } from './search-bar';

jest.useFakeTimers();

describe('SearchBar', () => {
  it('renders with placeholder', () => {
    render(<SearchBar value="" onChange={jest.fn()} placeholder="Search items..." />);
    expect(screen.getByPlaceholderText('Search items...')).toBeInTheDocument();
  });

  it('renders with current value', () => {
    render(<SearchBar value="hello" onChange={jest.fn()} />);
    expect(screen.getByDisplayValue('hello')).toBeInTheDocument();
  });

  it('calls onChange after debounce', async () => {
    const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
    const onChange = jest.fn();
    render(<SearchBar value="" onChange={onChange} debounceMs={300} />);

    await user.type(screen.getByRole('textbox'), 'test');

    // Before debounce fires
    expect(onChange).not.toHaveBeenCalled();

    // After debounce
    act(() => { jest.advanceTimersByTime(300); });
    expect(onChange).toHaveBeenCalledWith('test');
  });

  it('has search aria-label', () => {
    render(<SearchBar value="" onChange={jest.fn()} />);
    expect(screen.getByLabelText('Search')).toBeInTheDocument();
  });
});
