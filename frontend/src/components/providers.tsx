'use client';

import { ClerkProvider } from '@clerk/nextjs';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode, useState } from 'react';
import { ThemeProvider } from '@/contexts/theme-context';

interface ProvidersProps {
  children: ReactNode;
}

const clerkAppearance = {
  variables: {
    colorPrimary: '#2563eb',
    colorBackground: '#1f2937',
    colorText: '#ffffff',
    colorTextSecondary: '#9ca3af',
    colorInputBackground: '#374151',
    colorInputText: '#ffffff',
  },
};

// Check if a Clerk publishable key is valid (not a placeholder)
export function isValidClerkKey(key: string | undefined): boolean {
  if (!key) return false;
  // Valid Clerk keys start with pk_test_ or pk_live_ followed by base64-like chars
  // Placeholders like 'pk_test_placeholder' should be rejected
  return /^pk_(test|live)_[A-Za-z0-9]{20,}$/.test(key);
}

// Error message shown when Clerk is not configured
export function ClerkNotConfiguredError() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-900 p-8">
      <div className="max-w-md rounded-lg border border-red-500/50 bg-red-900/20 p-6 text-center">
        <h2 className="text-xl font-bold text-red-400">Clerk Not Configured</h2>
        <p className="mt-2 text-gray-300">
          Add your Clerk keys to <code className="rounded bg-gray-800 px-1">.env.local</code>:
        </p>
        <pre className="mt-4 rounded bg-gray-800 p-3 text-left text-sm text-gray-300">
{`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...`}
        </pre>
        <p className="mt-4 text-sm text-gray-400">
          Get keys at{' '}
          <a href="https://dashboard.clerk.com" className="text-blue-400 underline">
            dashboard.clerk.com
          </a>
        </p>
      </div>
    </div>
  );
}

export function Providers({ children }: ProvidersProps) {
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

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

  // If Clerk key is invalid, show error message
  if (!isValidClerkKey(publishableKey)) {
    return (
      <ThemeProvider>
        <QueryClientProvider client={queryClient}>
          <ClerkNotConfiguredError />
        </QueryClientProvider>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <ClerkProvider appearance={clerkAppearance}>
          {children}
        </ClerkProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
