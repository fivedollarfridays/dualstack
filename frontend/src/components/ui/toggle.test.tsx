/**
 * Tests for components/ui/toggle.tsx
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Toggle } from './toggle';

describe('Toggle', () => {
  const defaultProps = {
    checked: false,
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<Toggle {...defaultProps} />);
    expect(screen.getByRole('switch')).toBeInTheDocument();
  });

  it('renders unchecked state', () => {
    render(<Toggle {...defaultProps} checked={false} />);
    const toggle = screen.getByRole('switch');
    expect(toggle).toHaveAttribute('aria-checked', 'false');
  });

  it('renders checked state', () => {
    render(<Toggle {...defaultProps} checked={true} />);
    const toggle = screen.getByRole('switch');
    expect(toggle).toHaveAttribute('aria-checked', 'true');
  });

  it('calls onChange when clicked', async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    render(<Toggle checked={false} onChange={onChange} />);

    await user.click(screen.getByRole('switch'));
    expect(onChange).toHaveBeenCalledWith(true);
  });

  it('calls onChange with false when checked toggle is clicked', async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    render(<Toggle checked={true} onChange={onChange} />);

    await user.click(screen.getByRole('switch'));
    expect(onChange).toHaveBeenCalledWith(false);
  });

  it('does not call onChange when disabled', async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    render(<Toggle checked={false} onChange={onChange} disabled />);

    await user.click(screen.getByRole('switch'));
    expect(onChange).not.toHaveBeenCalled();
  });

  it('renders label text when provided', () => {
    render(<Toggle {...defaultProps} label="Enable feature" />);
    expect(screen.getByText('Enable feature')).toBeInTheDocument();
  });

  it('toggles when label is clicked', async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    render(<Toggle checked={false} onChange={onChange} label="Feature" />);

    await user.click(screen.getByText('Feature'));
    expect(onChange).toHaveBeenCalledWith(true);
  });

  it('does not toggle when disabled label is clicked', async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    render(<Toggle checked={false} onChange={onChange} label="Feature" disabled />);

    await user.click(screen.getByText('Feature'));
    expect(onChange).not.toHaveBeenCalled();
  });

  it('sets aria-label from ariaLabel prop', () => {
    render(<Toggle {...defaultProps} ariaLabel="Custom A11y label" />);
    const toggle = screen.getByRole('switch');
    expect(toggle).toHaveAttribute('aria-label', 'Custom A11y label');
  });

  it('uses label as aria-label fallback', () => {
    render(<Toggle {...defaultProps} label="Enable" />);
    const toggle = screen.getByRole('switch');
    expect(toggle).toHaveAttribute('aria-label', 'Enable');
  });

  it('sets aria-disabled when disabled', () => {
    render(<Toggle {...defaultProps} disabled />);
    const toggle = screen.getByRole('switch');
    expect(toggle).toHaveAttribute('aria-disabled', 'true');
  });

  it('sets tabIndex to -1 when disabled', () => {
    render(<Toggle {...defaultProps} disabled />);
    const toggle = screen.getByRole('switch');
    expect(toggle).toHaveAttribute('tabindex', '-1');
  });

  it('sets tabIndex to 0 when enabled', () => {
    render(<Toggle {...defaultProps} />);
    const toggle = screen.getByRole('switch');
    expect(toggle).toHaveAttribute('tabindex', '0');
  });

  it('toggles on Space key', () => {
    const onChange = jest.fn();
    render(<Toggle checked={false} onChange={onChange} />);
    const toggle = screen.getByRole('switch');

    fireEvent.keyDown(toggle, { key: ' ' });
    expect(onChange).toHaveBeenCalledWith(true);
  });

  it('toggles on Enter key', () => {
    const onChange = jest.fn();
    render(<Toggle checked={false} onChange={onChange} />);
    const toggle = screen.getByRole('switch');

    fireEvent.keyDown(toggle, { key: 'Enter' });
    expect(onChange).toHaveBeenCalledWith(true);
  });

  it('does not toggle on other keys', () => {
    const onChange = jest.fn();
    render(<Toggle checked={false} onChange={onChange} />);
    const toggle = screen.getByRole('switch');

    fireEvent.keyDown(toggle, { key: 'Tab' });
    expect(onChange).not.toHaveBeenCalled();
  });

  it('does not toggle on key when disabled', () => {
    const onChange = jest.fn();
    render(<Toggle checked={false} onChange={onChange} disabled />);
    const toggle = screen.getByRole('switch');

    fireEvent.keyDown(toggle, { key: ' ' });
    expect(onChange).not.toHaveBeenCalled();
  });

  it('accepts custom className', () => {
    const { container } = render(
      <Toggle {...defaultProps} className="custom-class" />
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
