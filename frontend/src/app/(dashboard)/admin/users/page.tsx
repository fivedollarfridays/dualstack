'use client';

import { useCallback, useState } from 'react';
import { UserTable } from '@/components/admin/user-table';
import { SearchBar } from '@/components/items/search-bar';
import { useAdminUsers, useUpdateUserRole } from '@/hooks/use-admin';

export default function AdminUsersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const { data, isLoading } = useAdminUsers(page, 20, search || undefined);
  const updateRole = useUpdateUserRole();

  const handleRoleChange = (userId: string, role: string) => {
    updateRole.mutate({ userId, role });
  };

  const handleSearchChange = useCallback((value: string) => {
    setSearch(value);
    setPage(1);
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold text-white">User Management</h1>
      <p className="mt-2 text-gray-400">Manage user roles and view user details.</p>

      <div className="mt-6">
        <SearchBar value={search} onChange={handleSearchChange} placeholder="Search users..." />
      </div>

      <div className="mt-6">
        {isLoading ? (
          <p className="text-gray-400">Loading users...</p>
        ) : (
          <>
            <UserTable users={data?.users ?? []} onRoleChange={handleRoleChange} />
            {data && data.total > 20 && (
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="rounded bg-gray-700 px-3 py-1 text-sm text-white disabled:opacity-50"
                >
                  Previous
                </button>
                <span className="px-2 py-1 text-sm text-gray-400">Page {page}</span>
                <button
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page * 20 >= data.total}
                  className="rounded bg-gray-700 px-3 py-1 text-sm text-white disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
