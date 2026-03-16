'use client';

import { ClerkProvider } from '@clerk/nextjs';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { ReactNode, useState } from 'react';
import { ThemeProvider } from '@/contexts/theme-context';
import { clerkAppearance } from '@/lib/clerk-config';
import { isClerkEnabled } from '@/lib/auth-config';
import { ClerkAuthBridge } from '@/components/auth/clerk-auth-bridge';
import { DevAuthProvider } from '@/components/auth/dev-auth-provider';

interface ProvidersProps {
  children: ReactNode;
  nonce?: string;
}

export function Providers({ children, nonce }: ProvidersProps) {
  // Create QueryClient with caching defaults for performance
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            gcTime: 5 * 60 * 1000, // 5 minutes (formerly cacheTime)
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  const clerkEnabled = isClerkEnabled();

  if (clerkEnabled) {
    return (
      <ThemeProvider>
        <QueryClientProvider client={queryClient}>
          <Toaster />
          <ClerkProvider appearance={clerkAppearance} nonce={nonce}>
            <ClerkAuthBridge>
              {children}
            </ClerkAuthBridge>
          </ClerkProvider>
        </QueryClientProvider>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <Toaster />
        <DevAuthProvider>
          {children}
        </DevAuthProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
