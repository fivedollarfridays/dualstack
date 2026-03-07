/**
 * Tests for components/auth/dev-sign-in.tsx (re-export of DevAuthCard)
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { DevSignIn } from './dev-sign-in';


describe('DevSignIn', () => {
  it('renders dev mode heading', () => {
    render(<DevSignIn />);
    expect(screen.getByText('Dev Mode')).toBeInTheDocument();
  });

  it('renders continue to dashboard link', () => {
    render(<DevSignIn />);
    const link = screen.getByRole('link', { name: /continue to dashboard/i });
    expect(link).toHaveAttribute('href', '/dashboard');
  });
});
