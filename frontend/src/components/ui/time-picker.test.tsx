/**
 * Tests for components/ui/time-picker.tsx
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TimePicker } from './time-picker';

describe('TimePicker', () => {
  const defaultProps = {
    value: '09:30',
    onChange: jest.fn(),
    label: 'Start Time',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<TimePicker {...defaultProps} />);
    expect(screen.getByText('Start Time')).toBeInTheDocument();
  });

  it('displays the initial time value', () => {
    render(<TimePicker {...defaultProps} />);
    const input = screen.getByDisplayValue('09:30');
    expect(input).toBeInTheDocument();
  });

  it('renders the label', () => {
    render(<TimePicker {...defaultProps} />);
    expect(screen.getByText('Start Time')).toBeInTheDocument();
  });

  it('shows placeholder HH:MM', () => {
    render(<TimePicker {...defaultProps} />);
    const input = screen.getByPlaceholderText('HH:MM');
    expect(input).toBeInTheDocument();
  });

  it('calls onChange with valid time on blur', async () => {
    const onChange = jest.fn();
    render(<TimePicker value="09:30" onChange={onChange} label="Time" />);
    const input = screen.getByDisplayValue('09:30');

    // Clear and type a new valid time
    await userEvent.clear(input);
    await userEvent.type(input, '14:45');
    fireEvent.blur(input);

    expect(onChange).toHaveBeenCalledWith('14:45');
  });

  it('shows error for invalid time format on blur', async () => {
    const onChange = jest.fn();
    render(<TimePicker value="09:30" onChange={onChange} label="Time" />);
    const input = screen.getByDisplayValue('09:30');

    await userEvent.clear(input);
    await userEvent.type(input, 'not-a-time');
    fireEvent.blur(input);

    expect(onChange).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent('Invalid time format');
  });

  it('shows error for invalid hour (25:00)', async () => {
    const onChange = jest.fn();
    render(<TimePicker value="09:30" onChange={onChange} label="Time" />);
    const input = screen.getByDisplayValue('09:30');

    await userEvent.clear(input);
    await userEvent.type(input, '25:00');
    fireEvent.blur(input);

    expect(onChange).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent('Hour must be 00-23');
  });

  it('shows error for invalid minute (12:60)', async () => {
    const onChange = jest.fn();
    render(<TimePicker value="09:30" onChange={onChange} label="Time" />);
    const input = screen.getByDisplayValue('09:30');

    await userEvent.clear(input);
    await userEvent.type(input, '12:60');
    fireEvent.blur(input);

    expect(onChange).not.toHaveBeenCalled();
    expect(screen.getByRole('alert')).toHaveTextContent('Minute must be 00-59');
  });

  it('does not call onChange when blurred with unchanged value', () => {
    const onChange = jest.fn();
    render(<TimePicker value="09:30" onChange={onChange} label="Time" />);
    const input = screen.getByDisplayValue('09:30');

    fireEvent.blur(input);

    expect(onChange).not.toHaveBeenCalled();
  });

  it('sets aria-invalid when there is an error', async () => {
    render(<TimePicker value="09:30" onChange={jest.fn()} label="Time" />);
    const input = screen.getByDisplayValue('09:30');

    await userEvent.clear(input);
    await userEvent.type(input, 'bad');
    fireEvent.blur(input);

    expect(input).toHaveAttribute('aria-invalid', 'true');
  });

  it('renders as disabled when disabled prop is set', () => {
    render(<TimePicker {...defaultProps} disabled />);
    const input = screen.getByDisplayValue('09:30');
    expect(input).toBeDisabled();
  });

  it('accepts custom className', () => {
    const { container } = render(
      <TimePicker {...defaultProps} className="my-class" />
    );
    expect(container.firstChild).toHaveClass('my-class');
  });

  it('updates local value on input change', async () => {
    render(<TimePicker {...defaultProps} />);
    const input = screen.getByDisplayValue('09:30');

    await userEvent.clear(input);
    await userEvent.type(input, '10:00');

    expect(input).toHaveValue('10:00');
  });

  it('clears error after entering a valid time', async () => {
    const onChange = jest.fn();
    render(<TimePicker value="09:30" onChange={onChange} label="Time" />);
    const input = screen.getByDisplayValue('09:30');

    // First enter invalid time
    await userEvent.clear(input);
    await userEvent.type(input, 'bad');
    fireEvent.blur(input);
    expect(screen.getByRole('alert')).toBeInTheDocument();

    // Then enter valid time
    await userEvent.clear(input);
    await userEvent.type(input, '10:00');
    fireEvent.blur(input);

    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(onChange).toHaveBeenCalledWith('10:00');
  });
});
