/**
 * Tests for components/ui/tooltip.tsx
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Tooltip } from './tooltip';

describe('Tooltip', () => {
  it('renders trigger content', () => {
    render(
      <Tooltip content="Help text">
        <button>Hover me</button>
      </Tooltip>
    );
    expect(screen.getByText('Hover me')).toBeInTheDocument();
  });

  it('does not show tooltip content by default', () => {
    render(
      <Tooltip content="Help text">
        <button>Hover me</button>
      </Tooltip>
    );
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  it('shows tooltip on mouse enter', () => {
    render(
      <Tooltip content="Help text">
        <button>Hover me</button>
      </Tooltip>
    );

    fireEvent.mouseEnter(screen.getByText('Hover me').parentElement!);
    expect(screen.getByRole('tooltip')).toHaveTextContent('Help text');
  });

  it('hides tooltip on mouse leave', () => {
    render(
      <Tooltip content="Help text">
        <button>Hover me</button>
      </Tooltip>
    );

    const container = screen.getByText('Hover me').parentElement!;

    fireEvent.mouseEnter(container);
    expect(screen.getByRole('tooltip')).toBeInTheDocument();

    fireEvent.mouseLeave(container);
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  it('accepts custom className', () => {
    const { container } = render(
      <Tooltip content="Help text" className="custom-tip">
        <span>text</span>
      </Tooltip>
    );
    expect(container.firstChild).toHaveClass('custom-tip');
  });

  it('renders children inside an inline-block wrapper', () => {
    const { container } = render(
      <Tooltip content="Help text">
        <span>text</span>
      </Tooltip>
    );
    expect(container.firstChild).toHaveClass('inline-block');
  });
});
