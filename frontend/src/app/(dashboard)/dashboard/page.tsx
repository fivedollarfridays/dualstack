'use client';

import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { useItems } from '@/hooks/use-items';
import { useSubscription } from '@/hooks/use-subscription';
import { capitalize } from '@/lib/utils';

export default function DashboardPage() {
  const { data, isLoading } = useItems(1, 1);
  const { plan, status, isLoading: subLoading } = useSubscription();
  const isFree = plan === 'free';

  return (
    <div>
      <h1 className="text-2xl font-bold text-white">Dashboard</h1>
      <p className="mt-2 text-gray-400">Welcome to your DualStack dashboard.</p>

      <div className="mt-8 grid gap-6 sm:grid-cols-2">
        {/* Items card */}
        <Card>
          <h3 className="text-sm font-medium text-gray-400">Items</h3>
          <p className="mt-2 text-3xl font-bold text-white">
            {isLoading ? '…' : (data?.total ?? 0)}
          </p>
          <p className="mt-1 text-sm text-gray-500">Total items created</p>
        </Card>

        {/* Subscription card */}
        <Card>
          <h3 className="text-sm font-medium text-gray-400">Subscription</h3>
          <p className="mt-2 text-3xl font-bold text-white">
            {subLoading ? '…' : capitalize(plan)}
          </p>
          <p className="mt-1 text-sm text-gray-500">
            {!subLoading && status !== 'none' ? capitalize(status) : 'Current plan'}
          </p>
          <div className="mt-3">
            <Link href="/billing" className="text-sm text-blue-400 hover:text-blue-300">
              {isFree ? 'Upgrade' : 'Manage Subscription'}
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
