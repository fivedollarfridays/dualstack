'use client';

import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { useAdminHealth } from '@/hooks/use-admin';

export default function AdminDashboardPage() {
  const { data: health, isLoading } = useAdminHealth();

  return (
    <div>
      <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
      <p className="mt-2 text-gray-400">System overview and management tools.</p>

      <div className="mt-8 grid gap-6 sm:grid-cols-3">
        <Card>
          <h3 className="text-sm font-medium text-gray-400">System Status</h3>
          <p className="mt-2 text-3xl font-bold text-white">
            {isLoading ? '...' : health?.status ?? 'unknown'}
          </p>
          <div className="mt-3">
            <Link href="/admin/health" className="text-sm text-blue-400 hover:text-blue-300">
              View Details
            </Link>
          </div>
        </Card>

        <Card>
          <h3 className="text-sm font-medium text-gray-400">Total Users</h3>
          <p className="mt-2 text-3xl font-bold text-white">
            {isLoading ? '...' : health?.user_count ?? 0}
          </p>
          <div className="mt-3">
            <Link href="/admin/users" className="text-sm text-blue-400 hover:text-blue-300">
              Manage Users
            </Link>
          </div>
        </Card>

        <Card>
          <h3 className="text-sm font-medium text-gray-400">Audit Log</h3>
          <p className="mt-2 text-3xl font-bold text-white">Events</p>
          <div className="mt-3">
            <Link href="/admin/audit" className="text-sm text-blue-400 hover:text-blue-300">
              View Logs
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
