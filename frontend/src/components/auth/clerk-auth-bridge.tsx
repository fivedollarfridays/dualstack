'use client';

import { ReactNode, useMemo, useCallback } from 'react';
import { useAuth } from '@clerk/nextjs';
import { AuthContext } from '@/contexts/auth-context';

/**
 * Bridges Clerk's useAuth() into AuthContext so all consumers
 * use the same useAppAuth() hook regardless of auth provider.
 */
export function ClerkAuthBridge({ children }: { children: ReactNode }) {
  const { userId, isLoaded, isSignedIn, getToken } = useAuth();

  const wrappedGetToken = useCallback(async () => {
    const token = await getToken();
    return token ?? null;
  }, [getToken]);

  const value = useMemo(() => ({
    userId: userId ?? null,
    isLoaded,
    isSignedIn: isSignedIn ?? false,
    getToken: wrappedGetToken,
  }), [userId, isLoaded, isSignedIn, wrappedGetToken]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
