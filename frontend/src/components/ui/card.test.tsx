import React from 'react';
import { render, screen } from '@testing-library/react';
import { Card } from './card';

describe('Card', () => {
  it('renders children', () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('applies default card classes', () => {
    render(<Card>content</Card>);
    const card = screen.getByText('content');
    expect(card).toHaveClass('rounded-lg', 'border', 'border-gray-700', 'bg-gray-800', 'p-6');
  });

  it('merges custom className', () => {
    render(<Card className="text-center">content</Card>);
    const card = screen.getByText('content');
    expect(card).toHaveClass('text-center');
    expect(card).toHaveClass('rounded-lg');
  });

  it('forwards additional HTML attributes', () => {
    render(<Card data-testid="my-card">content</Card>);
    expect(screen.getByTestId('my-card')).toBeInTheDocument();
  });
});
