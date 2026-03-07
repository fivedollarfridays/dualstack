/**
 * Tests for components/auth/clerk-auth-bridge.tsx
 */
import React from 'react';
import { renderHook } from '@testing-library/react';
import { ClerkAuthBridge } from './clerk-auth-bridge';
import { useAppAuth } from '@/contexts/auth-context';

// Mutable mock values so we can change per test
const mockValues = {
  userId: 'clerk-user-123' as string | undefined,
  isLoaded: true,
  isSignedIn: true as boolean | undefined,
  getToken: jest.fn().mockResolvedValue('clerk-token'),
};

jest.mock('@clerk/nextjs', () => ({
  useAuth: () => mockValues,
  useUser: () => ({ user: { id: 'clerk-user-123' }, isLoaded: true, isSignedIn: true }),
  useClerk: () => ({ signOut: jest.fn() }),
  ClerkProvider: ({ children }: { children: React.ReactNode }) => children,
  SignedIn: ({ children }: { children: React.ReactNode }) => children,
  SignedOut: () => null,
  UserButton: () => null,
}));

function renderWithBridge() {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <ClerkAuthBridge>{children}</ClerkAuthBridge>
  );
  return renderHook(() => useAppAuth(), { wrapper });
}

beforeEach(() => {
  mockValues.userId = 'clerk-user-123';
  mockValues.isLoaded = true;
  mockValues.isSignedIn = true;
  mockValues.getToken = jest.fn().mockResolvedValue('clerk-token');
});

describe('ClerkAuthBridge', () => {
  it('passes Clerk userId to AuthContext', () => {
    const { result } = renderWithBridge();
    expect(result.current.userId).toBe('clerk-user-123');
  });

  it('passes Clerk isLoaded to AuthContext', () => {
    const { result } = renderWithBridge();
    expect(result.current.isLoaded).toBe(true);
  });

  it('passes Clerk isSignedIn to AuthContext', () => {
    const { result } = renderWithBridge();
    expect(result.current.isSignedIn).toBe(true);
  });

  it('passes Clerk getToken to AuthContext', async () => {
    const { result } = renderWithBridge();
    const token = await result.current.getToken();
    expect(token).toBe('clerk-token');
  });

  it('defaults userId to null when Clerk returns undefined', () => {
    mockValues.userId = undefined;
    const { result } = renderWithBridge();
    expect(result.current.userId).toBeNull();
  });

  it('defaults isSignedIn to false when Clerk returns undefined', () => {
    mockValues.isSignedIn = undefined;
    const { result } = renderWithBridge();
    expect(result.current.isSignedIn).toBe(false);
  });

  it('defaults getToken result to null when Clerk returns null', async () => {
    mockValues.getToken = jest.fn().mockResolvedValue(null);
    const { result } = renderWithBridge();
    const token = await result.current.getToken();
    expect(token).toBeNull();
  });
});
