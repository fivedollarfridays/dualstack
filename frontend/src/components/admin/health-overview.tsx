'use client';

import { Card } from '@/components/ui/card';
import type { HealthResponse } from '@/lib/api/admin';

interface HealthOverviewProps {
  health: HealthResponse;
}

export function HealthOverview({ health }: HealthOverviewProps) {
  const isHealthy = health.status === 'healthy';

  return (
    <div className="grid gap-6 sm:grid-cols-3">
      <Card>
        <h3 className="text-sm font-medium text-gray-400">Status</h3>
        <p className={`mt-2 text-2xl font-bold ${isHealthy ? 'text-green-400' : 'text-red-400'}`}>
          {health.status}
        </p>
      </Card>

      <Card>
        <h3 className="text-sm font-medium text-gray-400">Database</h3>
        <p className="mt-2 text-2xl font-bold text-white">{health.database}</p>
      </Card>

      <Card>
        <h3 className="text-sm font-medium text-gray-400">Total Users</h3>
        <p className="mt-2 text-2xl font-bold text-white">{health.user_count}</p>
      </Card>
    </div>
  );
}
