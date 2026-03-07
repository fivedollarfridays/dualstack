/**
 * Tests for components/auth/dev-user-button.tsx
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { DevUserButton } from './dev-user-button';

describe('DevUserButton', () => {
  it('renders a circle with the letter D', () => {
    render(<DevUserButton />);
    expect(screen.getByText('D')).toBeInTheDocument();
  });

  it('renders with dev mode label', () => {
    render(<DevUserButton />);
    expect(screen.getByTitle('Dev Mode')).toBeInTheDocument();
  });
});
