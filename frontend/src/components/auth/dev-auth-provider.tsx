'use client';

import { ReactNode } from 'react';
import { AuthContext, AuthContextValue } from '@/contexts/auth-context';
import { DEV_USER_ID, DEV_TOKEN } from '@/lib/auth-config';

const DEV_AUTH_VALUE: AuthContextValue = {
  userId: DEV_USER_ID,
  isLoaded: true,
  isSignedIn: true,
  getToken: async () => DEV_TOKEN,
};

/**
 * Provides mock auth values for dev mode (no Clerk keys configured).
 */
export function DevAuthProvider({ children }: { children: ReactNode }) {
  return (
    <AuthContext.Provider value={DEV_AUTH_VALUE}>
      {children}
    </AuthContext.Provider>
  );
}
