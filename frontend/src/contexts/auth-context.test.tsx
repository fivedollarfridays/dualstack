/**
 * Tests for contexts/auth-context.tsx -- AuthContext and useAppAuth hook
 */
import React from 'react';
import { renderHook } from '@testing-library/react';
import { AuthContext, useAppAuth, AuthContextValue } from './auth-context';

describe('useAppAuth', () => {
  it('throws when used outside AuthContext provider', () => {
    expect(() => {
      renderHook(() => useAppAuth());
    }).toThrow('useAppAuth must be used within an AuthContext provider');
  });

  it('returns context value when inside provider', () => {
    const mockGetToken = jest.fn().mockResolvedValue('test-token');
    const value: AuthContextValue = {
      userId: 'user-123',
      isLoaded: true,
      isSignedIn: true,
      getToken: mockGetToken,
    };

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    );

    const { result } = renderHook(() => useAppAuth(), { wrapper });

    expect(result.current.userId).toBe('user-123');
    expect(result.current.isLoaded).toBe(true);
    expect(result.current.isSignedIn).toBe(true);
    expect(result.current.getToken).toBe(mockGetToken);
  });

  it('returns null userId when not signed in', () => {
    const value: AuthContextValue = {
      userId: null,
      isLoaded: true,
      isSignedIn: false,
      getToken: jest.fn().mockResolvedValue(null),
    };

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    );

    const { result } = renderHook(() => useAppAuth(), { wrapper });

    expect(result.current.userId).toBeNull();
    expect(result.current.isSignedIn).toBe(false);
  });
});
