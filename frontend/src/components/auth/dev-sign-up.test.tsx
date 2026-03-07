/**
 * Tests for components/auth/dev-sign-up.tsx (re-export of DevAuthCard)
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { DevSignUp } from './dev-sign-up';


describe('DevSignUp', () => {
  it('renders dev mode heading', () => {
    render(<DevSignUp />);
    expect(screen.getByText('Dev Mode')).toBeInTheDocument();
  });

  it('renders continue to dashboard link', () => {
    render(<DevSignUp />);
    const link = screen.getByRole('link', { name: /continue to dashboard/i });
    expect(link).toHaveAttribute('href', '/dashboard');
  });
});
