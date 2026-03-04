/**
 * Tests for app/sign-up/[[...sign-up]]/page.tsx — Sign up page
 */
import React from 'react';
import { render, screen } from '@testing-library/react';

// Override the global Clerk mock to include SignUp component
jest.mock('@clerk/nextjs', () => ({
  useUser: () => ({ user: { id: 'test-user-123' }, isLoaded: true, isSignedIn: true }),
  useAuth: () => ({ userId: 'test-user-123', isLoaded: true, isSignedIn: true }),
  useClerk: () => ({ signOut: jest.fn() }),
  ClerkProvider: ({ children }: { children: React.ReactNode }) => children,
  SignedIn: ({ children }: { children: React.ReactNode }) => children,
  SignedOut: ({ children }: { children: React.ReactNode }) => null,
  UserButton: () => null,
  SignUp: () => React.createElement('div', { 'data-testid': 'clerk-sign-up' }, 'Sign Up Form'),
}));

import SignUpPage from './page';

describe('SignUpPage', () => {
  it('renders the page heading', () => {
    render(<SignUpPage />);
    expect(screen.getByText('Get Started')).toBeInTheDocument();
  });

  it('renders the subtitle', () => {
    render(<SignUpPage />);
    expect(screen.getByText('Create your account')).toBeInTheDocument();
  });

  it('renders the Clerk SignUp component', () => {
    render(<SignUpPage />);
    expect(screen.getByTestId('clerk-sign-up')).toBeInTheDocument();
  });
});
