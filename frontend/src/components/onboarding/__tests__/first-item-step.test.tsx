/**
 * Tests for FirstItemStep component.
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { FirstItemStep } from '../first-item-step';

describe('FirstItemStep', () => {
  it('renders heading and simplified item creation form', () => {
    render(<FirstItemStep onCreated={jest.fn()} />);

    expect(screen.getByRole('heading', { name: /first item/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create/i })).toBeInTheDocument();
  });

  it('calls onCreated with title when form submitted', () => {
    const onCreated = jest.fn();
    render(<FirstItemStep onCreated={onCreated} />);

    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'My first item' },
    });
    fireEvent.click(screen.getByRole('button', { name: /create/i }));

    expect(onCreated).toHaveBeenCalledWith('My first item');
  });

  it('does not call onCreated when title is empty', () => {
    const onCreated = jest.fn();
    render(<FirstItemStep onCreated={onCreated} />);

    fireEvent.click(screen.getByRole('button', { name: /create/i }));

    expect(onCreated).not.toHaveBeenCalled();
  });
});
