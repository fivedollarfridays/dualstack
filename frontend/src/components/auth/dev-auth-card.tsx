'use client';

import Link from 'next/link';
import { Card } from '@/components/ui/card';

/**
 * Shared dev-mode card for sign-in and sign-up pages.
 * Shows a "Continue to Dashboard" link when Clerk is not configured.
 */
export function DevAuthCard() {
  return (
    <Card className="text-center">
      <h2 className="text-xl font-bold text-white">Dev Mode</h2>
      <p className="mt-2 text-gray-400">Auth is bypassed. No Clerk keys configured.</p>
      <Link
        href="/dashboard"
        className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-500"
      >
        Continue to Dashboard
      </Link>
    </Card>
  );
}
