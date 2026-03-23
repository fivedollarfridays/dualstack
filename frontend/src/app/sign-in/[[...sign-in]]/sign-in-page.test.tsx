/**
 * Tests for app/sign-in/[[...sign-in]]/page.tsx — Sign in page
 */
import React from 'react';
import { render, screen } from '@testing-library/react';

jest.mock('@clerk/nextjs', () => ({
  useUser: () => ({ user: { id: 'test-user-123' }, isLoaded: true, isSignedIn: true }),
  useAuth: () => ({ userId: 'test-user-123', isLoaded: true, isSignedIn: true }),
  useClerk: () => ({ signOut: jest.fn() }),
  ClerkProvider: ({ children }: { children: React.ReactNode }) => children,
  SignedIn: ({ children }: { children: React.ReactNode }) => children,
  SignedOut: () => null,
  UserButton: () => null,
  SignIn: () => React.createElement('div', { 'data-testid': 'clerk-sign-in' }, 'Sign In Form'),
}));

jest.mock('@/lib/auth-config', () => ({
  isClerkEnabled: jest.fn(),
  DEV_USER_ID: 'dev-user-001',
  DEV_TOKEN: 'mock-dev-token',
  getDevToken: jest.fn(() => 'mock-dev-token'),
  isLocalDev: jest.fn(() => true),
}));

import { isClerkEnabled } from '@/lib/auth-config';
const mockIsClerkEnabled = isClerkEnabled as jest.MockedFunction<typeof isClerkEnabled>;

import SignInPage from './page';

beforeEach(() => {
  jest.clearAllMocks();
});

describe('SignInPage', () => {
  it('renders the page heading', () => {
    mockIsClerkEnabled.mockReturnValue(true);
    render(<SignInPage />);
    expect(screen.getByText('Welcome Back')).toBeInTheDocument();
  });

  it('renders the subtitle', () => {
    mockIsClerkEnabled.mockReturnValue(true);
    render(<SignInPage />);
    expect(screen.getByText('Sign in to continue')).toBeInTheDocument();
  });

  it('renders the Clerk SignIn component when Clerk is enabled', () => {
    mockIsClerkEnabled.mockReturnValue(true);
    render(<SignInPage />);
    expect(screen.getByTestId('clerk-sign-in')).toBeInTheDocument();
  });

  it('renders dev sign-in card when Clerk is disabled', () => {
    mockIsClerkEnabled.mockReturnValue(false);
    render(<SignInPage />);
    expect(screen.getByText('Dev Mode')).toBeInTheDocument();
    expect(screen.getByText('Continue to Dashboard')).toBeInTheDocument();
  });

  it('does not render Clerk SignIn when Clerk is disabled', () => {
    mockIsClerkEnabled.mockReturnValue(false);
    render(<SignInPage />);
    expect(screen.queryByTestId('clerk-sign-in')).not.toBeInTheDocument();
  });
});
