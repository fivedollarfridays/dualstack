/**
 * Tests for components/ui/slider.tsx
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Slider } from './slider';

describe('Slider', () => {
  const defaultProps = {
    value: 50,
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<Slider {...defaultProps} />);
    expect(screen.getByRole('slider')).toBeInTheDocument();
  });

  it('renders with the correct value', () => {
    render(<Slider {...defaultProps} />);
    const slider = screen.getByRole('slider');
    expect(slider).toHaveValue('50');
  });

  it('renders with custom min, max, and step', () => {
    render(<Slider {...defaultProps} min={10} max={200} step={5} />);
    const slider = screen.getByRole('slider');
    expect(slider).toHaveAttribute('min', '10');
    expect(slider).toHaveAttribute('max', '200');
    expect(slider).toHaveAttribute('step', '5');
  });

  it('accepts custom className', () => {
    const { container } = render(
      <Slider {...defaultProps} className="my-custom-class" />
    );
    expect(container.firstChild).toHaveClass('my-custom-class');
  });

  it('renders label when provided', () => {
    render(<Slider {...defaultProps} label="Volume" />);
    expect(screen.getByText('Volume')).toBeInTheDocument();
  });

  it('shows value when showValue is true', () => {
    render(<Slider {...defaultProps} showValue />);
    expect(screen.getByText('50')).toBeInTheDocument();
  });

  it('uses valueFormatter when showValue is true and formatter provided', () => {
    render(
      <Slider
        {...defaultProps}
        showValue
        valueFormatter={(v) => `${v}%`}
      />
    );
    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  it('calls onChange on input change', () => {
    const onChange = jest.fn();
    render(<Slider {...defaultProps} onChange={onChange} />);
    const slider = screen.getByRole('slider');

    fireEvent.change(slider, { target: { value: '75' } });
    expect(onChange).toHaveBeenCalledWith(75);
  });

  it('calls onChange on input event', () => {
    const onChange = jest.fn();
    render(<Slider {...defaultProps} onChange={onChange} />);
    const slider = screen.getByRole('slider');

    fireEvent.input(slider, { target: { value: '30' } });
    expect(onChange).toHaveBeenCalledWith(30);
  });

  it('does not call onChange on change event when disabled', () => {
    const onChange = jest.fn();
    render(<Slider {...defaultProps} onChange={onChange} disabled />);
    const slider = screen.getByRole('slider');

    fireEvent.change(slider, { target: { value: '75' } });
    expect(onChange).not.toHaveBeenCalled();
  });

  it('does not call onChange on input event when disabled', () => {
    const onChange = jest.fn();
    render(<Slider {...defaultProps} onChange={onChange} disabled />);
    const slider = screen.getByRole('slider');

    fireEvent.input(slider, { target: { value: '75' } });
    expect(onChange).not.toHaveBeenCalled();
  });

  it('renders with disabled styling', () => {
    const { container } = render(<Slider {...defaultProps} disabled />);
    expect(container.firstChild).toHaveClass('opacity-50');
  });

  it('sets aria-label from ariaLabel prop', () => {
    render(<Slider {...defaultProps} aria-label="Custom label" />);
    const slider = screen.getByRole('slider');
    expect(slider).toHaveAttribute('aria-label', 'Custom label');
  });

  it('uses label as aria-label fallback', () => {
    render(<Slider {...defaultProps} label="Volume" />);
    const slider = screen.getByRole('slider');
    expect(slider).toHaveAttribute('aria-label', 'Volume');
  });

  it('handles ArrowRight keydown to increment', () => {
    const onChange = jest.fn();
    render(<Slider value={50} onChange={onChange} step={5} max={100} />);
    const slider = screen.getByRole('slider');

    fireEvent.keyDown(slider, { key: 'ArrowRight' });
    expect(onChange).toHaveBeenCalledWith(55);
  });

  it('handles ArrowUp keydown to increment', () => {
    const onChange = jest.fn();
    render(<Slider value={50} onChange={onChange} step={5} max={100} />);
    const slider = screen.getByRole('slider');

    fireEvent.keyDown(slider, { key: 'ArrowUp' });
    expect(onChange).toHaveBeenCalledWith(55);
  });

  it('handles ArrowLeft keydown to decrement', () => {
    const onChange = jest.fn();
    render(<Slider value={50} onChange={onChange} step={5} min={0} />);
    const slider = screen.getByRole('slider');

    fireEvent.keyDown(slider, { key: 'ArrowLeft' });
    expect(onChange).toHaveBeenCalledWith(45);
  });

  it('handles ArrowDown keydown to decrement', () => {
    const onChange = jest.fn();
    render(<Slider value={50} onChange={onChange} step={5} min={0} />);
    const slider = screen.getByRole('slider');

    fireEvent.keyDown(slider, { key: 'ArrowDown' });
    expect(onChange).toHaveBeenCalledWith(45);
  });

  it('clamps increment at max value', () => {
    const onChange = jest.fn();
    render(<Slider value={98} onChange={onChange} step={5} max={100} />);
    const slider = screen.getByRole('slider');

    fireEvent.keyDown(slider, { key: 'ArrowRight' });
    expect(onChange).toHaveBeenCalledWith(100);
  });

  it('clamps decrement at min value', () => {
    const onChange = jest.fn();
    render(<Slider value={2} onChange={onChange} step={5} min={0} />);
    const slider = screen.getByRole('slider');

    fireEvent.keyDown(slider, { key: 'ArrowLeft' });
    expect(onChange).toHaveBeenCalledWith(0);
  });

  it('does not call onChange for unrelated keys', () => {
    const onChange = jest.fn();
    render(<Slider value={50} onChange={onChange} />);
    const slider = screen.getByRole('slider');

    fireEvent.keyDown(slider, { key: 'Enter' });
    expect(onChange).not.toHaveBeenCalled();
  });

  it('does not call onChange on keydown when disabled', () => {
    const onChange = jest.fn();
    render(<Slider value={50} onChange={onChange} disabled />);
    const slider = screen.getByRole('slider');

    fireEvent.keyDown(slider, { key: 'ArrowRight' });
    expect(onChange).not.toHaveBeenCalled();
  });

  it('does not call onChange when value would not change at boundary', () => {
    const onChange = jest.fn();
    render(<Slider value={100} onChange={onChange} step={1} max={100} />);
    const slider = screen.getByRole('slider');

    fireEvent.keyDown(slider, { key: 'ArrowRight' });
    // value is already at max, newValue === value, so onChange should not be called
    expect(onChange).not.toHaveBeenCalled();
  });

  it('does not show value display by default', () => {
    render(<Slider {...defaultProps} />);
    // Without showValue, the value text should not appear in a separate span
    const valueSpans = screen.queryAllByText('50');
    // The input has value=50 but no visible span
    expect(valueSpans.length).toBe(0);
  });
});
