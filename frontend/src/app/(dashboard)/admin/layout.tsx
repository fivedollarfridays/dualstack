'use client';

import { useAdminHealth } from '@/hooks/use-admin';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { isLoading, isError, error } = useAdminHealth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (isError) {
    const isForbidden = error?.message?.includes('403') || error?.message?.includes('Insufficient');
    if (isForbidden) {
      return (
        <div data-testid="admin-forbidden">
          <h1 className="text-2xl font-bold text-white">Access Denied</h1>
          <p className="mt-2 text-gray-400">You need admin privileges to access this page.</p>
        </div>
      );
    }
    return (
      <div data-testid="admin-error">
        <h1 className="text-2xl font-bold text-white">Something went wrong</h1>
        <p className="mt-2 text-gray-400">Unable to load admin panel. Please try again later.</p>
      </div>
    );
  }

  return <>{children}</>;
}
