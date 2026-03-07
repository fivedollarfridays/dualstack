/**
 * Tests for components/auth/dev-auth-card.tsx
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { DevAuthCard } from './dev-auth-card';


describe('DevAuthCard', () => {
  it('renders dev mode heading', () => {
    render(<DevAuthCard />);
    expect(screen.getByText('Dev Mode')).toBeInTheDocument();
  });

  it('renders auth bypass message', () => {
    render(<DevAuthCard />);
    expect(screen.getByText('Auth is bypassed. No Clerk keys configured.')).toBeInTheDocument();
  });

  it('renders continue to dashboard link', () => {
    render(<DevAuthCard />);
    const link = screen.getByRole('link', { name: /continue to dashboard/i });
    expect(link).toHaveAttribute('href', '/dashboard');
  });
});
