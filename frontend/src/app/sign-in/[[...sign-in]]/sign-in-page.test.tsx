/**
 * Tests for app/sign-in/[[...sign-in]]/page.tsx — Sign in page
 */
import React from 'react';
import { render, screen } from '@testing-library/react';

// Override the global Clerk mock to include SignIn component
jest.mock('@clerk/nextjs', () => ({
  useUser: () => ({ user: { id: 'test-user-123' }, isLoaded: true, isSignedIn: true }),
  useAuth: () => ({ userId: 'test-user-123', isLoaded: true, isSignedIn: true }),
  useClerk: () => ({ signOut: jest.fn() }),
  ClerkProvider: ({ children }: { children: React.ReactNode }) => children,
  SignedIn: ({ children }: { children: React.ReactNode }) => children,
  SignedOut: ({ children }: { children: React.ReactNode }) => null,
  UserButton: () => null,
  SignIn: () => React.createElement('div', { 'data-testid': 'clerk-sign-in' }, 'Sign In Form'),
}));

import SignInPage from './page';

describe('SignInPage', () => {
  it('renders the page heading', () => {
    render(<SignInPage />);
    expect(screen.getByText('Welcome Back')).toBeInTheDocument();
  });

  it('renders the subtitle', () => {
    render(<SignInPage />);
    expect(screen.getByText('Sign in to continue')).toBeInTheDocument();
  });

  it('renders the Clerk SignIn component', () => {
    render(<SignInPage />);
    expect(screen.getByTestId('clerk-sign-in')).toBeInTheDocument();
  });
});
