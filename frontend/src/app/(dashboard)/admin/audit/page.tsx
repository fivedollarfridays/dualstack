'use client';

import { useState } from 'react';
import { AuditLog } from '@/components/admin/audit-log';
import { useAdminAuditLogs } from '@/hooks/use-admin';

export default function AdminAuditPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useAdminAuditLogs(page);

  return (
    <div>
      <h1 className="text-2xl font-bold text-white">Audit Log</h1>
      <p className="mt-2 text-gray-400">View system activity and security events.</p>

      <div className="mt-8">
        {isLoading ? (
          <p className="text-gray-400">Loading audit log...</p>
        ) : (
          <AuditLog
            entries={data?.entries ?? []}
            total={data?.total ?? 0}
            page={page}
            onPageChange={setPage}
          />
        )}
      </div>
    </div>
  );
}
