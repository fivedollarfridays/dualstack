'use client';

import { HealthOverview } from '@/components/admin/health-overview';
import { useAdminHealth } from '@/hooks/use-admin';

export default function AdminHealthPage() {
  const { data: health, isLoading } = useAdminHealth();

  return (
    <div>
      <h1 className="text-2xl font-bold text-white">System Health</h1>
      <p className="mt-2 text-gray-400">Monitor system status and key metrics.</p>

      <div className="mt-8">
        {isLoading ? (
          <p className="text-gray-400">Loading health data...</p>
        ) : health ? (
          <HealthOverview health={health} />
        ) : (
          <p className="text-gray-400">Unable to load health data.</p>
        )}
      </div>
    </div>
  );
}
