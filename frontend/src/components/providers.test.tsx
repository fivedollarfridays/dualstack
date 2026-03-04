/**
 * Tests for components/providers.tsx — Providers wrapper and Clerk key validation
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { isValidClerkKey, ClerkNotConfiguredError, Providers } from './providers';

// Store original env
const originalEnv = process.env;

beforeEach(() => {
  // Reset env for each test
  process.env = { ...originalEnv };

  // Mock matchMedia for ThemeProvider (used inside Providers)
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

describe('isValidClerkKey', () => {
  it('returns true for a valid test key', () => {
    expect(isValidClerkKey('pk_test_Y2xlcmsuZXhhbXBsZS5jb20k')).toBe(true);
  });

  it('returns true for a valid live key', () => {
    expect(isValidClerkKey('pk_live_Y2xlcmsuZXhhbXBsZS5jb20k')).toBe(true);
  });

  it('returns false for undefined', () => {
    expect(isValidClerkKey(undefined)).toBe(false);
  });

  it('returns false for empty string', () => {
    expect(isValidClerkKey('')).toBe(false);
  });

  it('returns false for a placeholder key', () => {
    expect(isValidClerkKey('pk_test_placeholder')).toBe(false);
  });

  it('returns false for a key with wrong prefix', () => {
    expect(isValidClerkKey('sk_test_Y2xlcmsuZXhhbXBsZS5jb20k')).toBe(false);
  });

  it('returns false for a key that is too short', () => {
    expect(isValidClerkKey('pk_test_abc')).toBe(false);
  });
});

describe('ClerkNotConfiguredError', () => {
  it('renders the error heading', () => {
    render(<ClerkNotConfiguredError />);
    expect(screen.getByText('Clerk Not Configured')).toBeInTheDocument();
  });

  it('renders instructions about .env.local', () => {
    render(<ClerkNotConfiguredError />);
    expect(screen.getByText('.env.local')).toBeInTheDocument();
  });

  it('renders link to Clerk dashboard', () => {
    render(<ClerkNotConfiguredError />);
    const link = screen.getByRole('link', { name: /dashboard\.clerk\.com/i });
    expect(link).toHaveAttribute('href', 'https://dashboard.clerk.com');
  });
});

describe('Providers', () => {
  it('shows ClerkNotConfiguredError when Clerk key is missing', () => {
    delete process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

    render(
      <Providers>
        <span>child content</span>
      </Providers>
    );

    expect(screen.getByText('Clerk Not Configured')).toBeInTheDocument();
    expect(screen.queryByText('child content')).not.toBeInTheDocument();
  });

  it('shows ClerkNotConfiguredError when Clerk key is a placeholder', () => {
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = 'pk_test_placeholder';

    render(
      <Providers>
        <span>child content</span>
      </Providers>
    );

    expect(screen.getByText('Clerk Not Configured')).toBeInTheDocument();
  });

  it('renders children when Clerk key is valid', () => {
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY =
      'pk_test_Y2xlcmsuZXhhbXBsZS5jb20k';

    render(
      <Providers>
        <span>child content</span>
      </Providers>
    );

    expect(screen.getByText('child content')).toBeInTheDocument();
    expect(screen.queryByText('Clerk Not Configured')).not.toBeInTheDocument();
  });
});
