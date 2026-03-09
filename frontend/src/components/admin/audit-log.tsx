'use client';

import type { AuditEntry } from '@/lib/api/admin';

interface AuditLogProps {
  entries: AuditEntry[];
  total: number;
  page: number;
  onPageChange: (page: number) => void;
  limit?: number;
}

export function AuditLog({ entries, total, page, onPageChange, limit = 50 }: AuditLogProps) {
  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-gray-300">
          <thead className="border-b border-gray-700 text-xs uppercase text-gray-400">
            <tr>
              <th className="px-4 py-3">Time</th>
              <th className="px-4 py-3">User</th>
              <th className="px-4 py-3">Action</th>
              <th className="px-4 py-3">Resource</th>
              <th className="px-4 py-3">Outcome</th>
              <th className="px-4 py-3">Detail</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr key={entry.id} className="border-b border-gray-700">
                <td className="px-4 py-3 text-xs">{new Date(entry.created_at).toLocaleString()}</td>
                <td className="px-4 py-3 font-mono text-xs">{entry.user_id}</td>
                <td className="px-4 py-3">{entry.action}</td>
                <td className="px-4 py-3">{entry.resource_type}/{entry.resource_id}</td>
                <td className="px-4 py-3">
                  <span className={`rounded px-2 py-1 text-xs font-medium ${
                    entry.outcome === 'success' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
                  }`}>
                    {entry.outcome}
                  </span>
                </td>
                <td className="px-4 py-3 text-xs text-gray-500">{entry.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {entries.length === 0 && (
          <p className="py-8 text-center text-gray-500">No audit log entries.</p>
        )}
      </div>

      {total > limit && (
        <div className="mt-4 flex items-center justify-between">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="rounded bg-gray-700 px-3 py-1 text-sm text-white disabled:opacity-50"
          >
            Previous
          </button>
          <span className="text-sm text-gray-400">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="rounded bg-gray-700 px-3 py-1 text-sm text-white disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
