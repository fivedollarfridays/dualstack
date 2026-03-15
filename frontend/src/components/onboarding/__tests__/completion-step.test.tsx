/**
 * Tests for CompletionStep component.
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { CompletionStep } from '../completion-step';

describe('CompletionStep', () => {
  it('renders success message', () => {
    render(<CompletionStep onFinish={jest.fn()} />);
    expect(screen.getByText(/all set/i)).toBeInTheDocument();
  });

  it('renders "Go to Dashboard" button that calls onFinish', () => {
    const onFinish = jest.fn();
    render(<CompletionStep onFinish={onFinish} />);

    const btn = screen.getByRole('button', { name: /go to dashboard/i });
    fireEvent.click(btn);
    expect(onFinish).toHaveBeenCalled();
  });
});
