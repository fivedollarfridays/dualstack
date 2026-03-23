/**
 * Tests for app/sign-up/[[...sign-up]]/page.tsx — Sign up page
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
  SignUp: () => React.createElement('div', { 'data-testid': 'clerk-sign-up' }, 'Sign Up Form'),
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

import SignUpPage from './page';

beforeEach(() => {
  jest.clearAllMocks();
});

describe('SignUpPage', () => {
  it('renders the page heading', () => {
    mockIsClerkEnabled.mockReturnValue(true);
    render(<SignUpPage />);
    expect(screen.getByText('Get Started')).toBeInTheDocument();
  });

  it('renders the subtitle', () => {
    mockIsClerkEnabled.mockReturnValue(true);
    render(<SignUpPage />);
    expect(screen.getByText('Create your account')).toBeInTheDocument();
  });

  it('renders the Clerk SignUp component when Clerk is enabled', () => {
    mockIsClerkEnabled.mockReturnValue(true);
    render(<SignUpPage />);
    expect(screen.getByTestId('clerk-sign-up')).toBeInTheDocument();
  });

  it('renders dev sign-up card when Clerk is disabled', () => {
    mockIsClerkEnabled.mockReturnValue(false);
    render(<SignUpPage />);
    expect(screen.getByText('Dev Mode')).toBeInTheDocument();
    expect(screen.getByText('Continue to Dashboard')).toBeInTheDocument();
  });

  it('does not render Clerk SignUp when Clerk is disabled', () => {
    mockIsClerkEnabled.mockReturnValue(false);
    render(<SignUpPage />);
    expect(screen.queryByTestId('clerk-sign-up')).not.toBeInTheDocument();
  });
});
