'use client';

import { createContext, useContext } from 'react';

export interface AuthContextValue {
  userId: string | null;
  isLoaded: boolean;
  isSignedIn: boolean;
  getToken: () => Promise<string | null>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function useAppAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAppAuth must be used within an AuthContext provider');
  }
  return context;
}
