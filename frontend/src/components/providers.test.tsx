/**
 * Tests for components/providers.tsx — Providers wrapper and Clerk key validation
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { Providers } from './providers';

// Store original env
const originalEnv = process.env;

// Mock the auth modules
jest.mock('@/lib/auth-config', () => ({
  isClerkEnabled: jest.fn(),
  DEV_USER_ID: 'dev-user-001',
  DEV_TOKEN: 'dev-token',
}));

jest.mock('@/components/auth/clerk-auth-bridge', () => ({
  ClerkAuthBridge: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="clerk-auth-bridge">{children}</div>
  ),
}));

jest.mock('@/components/auth/dev-auth-provider', () => ({
  DevAuthProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="dev-auth-provider">{children}</div>
  ),
}));

import { isClerkEnabled } from '@/lib/auth-config';
const mockIsClerkEnabled = isClerkEnabled as jest.MockedFunction<typeof isClerkEnabled>;

beforeEach(() => {
  process.env = { ...originalEnv };
  jest.clearAllMocks();

  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    })),
  });
});

afterAll(() => {
  process.env = originalEnv;
});

describe('Providers', () => {
  it('renders DevAuthProvider when Clerk is not enabled', () => {
    mockIsClerkEnabled.mockReturnValue(false);

    render(
      <Providers>
        <span>child content</span>
      </Providers>
    );

    expect(screen.getByTestId('dev-auth-provider')).toBeInTheDocument();
    expect(screen.getByText('child content')).toBeInTheDocument();
  });

  it('renders ClerkAuthBridge when Clerk is enabled', () => {
    mockIsClerkEnabled.mockReturnValue(true);
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY =
      'pk_test_Y2xlcmsuZXhhbXBsZS5jb20k';

    render(
      <Providers>
        <span>child content</span>
      </Providers>
    );

    expect(screen.getByTestId('clerk-auth-bridge')).toBeInTheDocument();
    expect(screen.getByText('child content')).toBeInTheDocument();
  });

  it('does not render ClerkAuthBridge when Clerk is disabled', () => {
    mockIsClerkEnabled.mockReturnValue(false);

    render(
      <Providers>
        <span>child content</span>
      </Providers>
    );

    expect(screen.queryByTestId('clerk-auth-bridge')).not.toBeInTheDocument();
  });

  it('does not render DevAuthProvider when Clerk is enabled', () => {
    mockIsClerkEnabled.mockReturnValue(true);
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY =
      'pk_test_Y2xlcmsuZXhhbXBsZS5jb20k';

    render(
      <Providers>
        <span>child content</span>
      </Providers>
    );

    expect(screen.queryByTestId('dev-auth-provider')).not.toBeInTheDocument();
  });
});
