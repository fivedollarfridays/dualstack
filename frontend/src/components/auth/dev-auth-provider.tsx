'use client';

import { ReactNode, useEffect } from 'react';
import { AuthContext, AuthContextValue } from '@/contexts/auth-context';
import { DEV_USER_ID, getDevToken } from '@/lib/auth-config';

const DEV_AUTH_VALUE: AuthContextValue = {
  userId: DEV_USER_ID,
  isLoaded: true,
  isSignedIn: true,
  getToken: async () => getDevToken() ?? '',
};

/**
 * Provides mock auth values for dev mode (no Clerk keys configured).
 */
export function DevAuthProvider({ children }: { children: ReactNode }) {
  if (process.env.NODE_ENV === 'production') {
    throw new Error(
      'DevAuthProvider must not be used in production. ' +
      'Set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY to enable real auth.'
    );
  }

  useEffect(() => {
    console.warn(
      '[DevAuthProvider] Dev auth mode is active. ' +
      'All requests use a hardcoded token. ' +
      'This is NOT compatible with production backends. ' +
      'Set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY to enable real auth.'
    );
  }, []);

  return (
    <AuthContext.Provider value={DEV_AUTH_VALUE}>
      {children}
    </AuthContext.Provider>
  );
}
