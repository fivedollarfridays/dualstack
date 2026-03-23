/**
 * Tests for components/auth/dev-auth-provider.tsx
 */
import React from 'react';
import { renderHook } from '@testing-library/react';
import { useAppAuth } from '@/contexts/auth-context';

// Keep a reference to allow overriding getDevToken per test
let mockDevToken: string | null = 'mock-random-token-abc123';
jest.mock('@/lib/auth-config', () => ({
  ...jest.requireActual('@/lib/auth-config'),
  getDevToken: () => mockDevToken,
}));

// Import after mock setup
import { DevAuthProvider } from './dev-auth-provider';

describe('DevAuthProvider', () => {
  it('provides dev user ID', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <DevAuthProvider>{children}</DevAuthProvider>
    );
    const { result } = renderHook(() => useAppAuth(), { wrapper });
    expect(result.current.userId).toBe('dev-user-001');
  });

  it('provides isLoaded as true', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <DevAuthProvider>{children}</DevAuthProvider>
    );
    const { result } = renderHook(() => useAppAuth(), { wrapper });
    expect(result.current.isLoaded).toBe(true);
  });

  it('provides isSignedIn as true', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <DevAuthProvider>{children}</DevAuthProvider>
    );
    const { result } = renderHook(() => useAppAuth(), { wrapper });
    expect(result.current.isSignedIn).toBe(true);
  });

  it('provides getToken that returns the mock dev token', async () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <DevAuthProvider>{children}</DevAuthProvider>
    );
    const { result } = renderHook(() => useAppAuth(), { wrapper });
    const token = await result.current.getToken();
    expect(token).toBe('mock-random-token-abc123');
  });

  it('logs a warning when active', () => {
    const spy = jest.spyOn(console, 'warn').mockImplementation(() => {});
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <DevAuthProvider>{children}</DevAuthProvider>
    );
    renderHook(() => useAppAuth(), { wrapper });
    expect(spy).toHaveBeenCalledWith(
      expect.stringContaining('[DevAuthProvider]')
    );
    spy.mockRestore();
  });

  it('returns empty string from getToken when getDevToken returns null', async () => {
    mockDevToken = null;
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <DevAuthProvider>{children}</DevAuthProvider>
    );
    const { result } = renderHook(() => useAppAuth(), { wrapper });
    const token = await result.current.getToken();
    expect(token).toBe('');
    mockDevToken = 'mock-random-token-abc123'; // restore
  });

  it('throws an error in production environment', () => {
    const originalEnv = process.env.NODE_ENV;
    try {
      Object.defineProperty(process.env, 'NODE_ENV', { value: 'production', configurable: true });
      expect(() => {
        const wrapper = ({ children }: { children: React.ReactNode }) => (
          <DevAuthProvider>{children}</DevAuthProvider>
        );
        renderHook(() => useAppAuth(), { wrapper });
      }).toThrow('DevAuthProvider must not be used in production');
    } finally {
      Object.defineProperty(process.env, 'NODE_ENV', { value: originalEnv, configurable: true });
    }
  });
});
