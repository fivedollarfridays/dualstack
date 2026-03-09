'use client';

import { useEffect, useState } from 'react';
import type { AdminUser } from '@/lib/api/admin';

interface UserTableProps {
  users: AdminUser[];
  onRoleChange: (userId: string, role: string) => void;
}

export function UserTable({ users, onRoleChange }: UserTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm text-gray-300">
        <thead className="border-b border-gray-700 text-xs uppercase text-gray-400">
          <tr>
            <th className="px-4 py-3">User ID</th>
            <th className="px-4 py-3">Role</th>
            <th className="px-4 py-3">Plan</th>
            <th className="px-4 py-3">Created</th>
            <th className="px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <UserRow key={user.id} user={user} onRoleChange={onRoleChange} />
          ))}
        </tbody>
      </table>
      {users.length === 0 && (
        <p className="py-8 text-center text-gray-500">No users found.</p>
      )}
    </div>
  );
}

function UserRow({
  user,
  onRoleChange,
}: {
  user: AdminUser;
  onRoleChange: (userId: string, role: string) => void;
}) {
  const [selectedRole, setSelectedRole] = useState(user.role);

  useEffect(() => {
    setSelectedRole(user.role);
  }, [user.role]);

  const handleChange = (newRole: string) => {
    setSelectedRole(newRole);
    onRoleChange(user.id, newRole);
  };

  return (
    <tr className="border-b border-gray-700">
      <td className="px-4 py-3 font-mono text-xs">{user.clerk_user_id}</td>
      <td className="px-4 py-3">
        <span className={`rounded px-2 py-1 text-xs font-medium ${
          user.role === 'admin' ? 'bg-blue-900 text-blue-300' : 'bg-gray-700 text-gray-300'
        }`}>
          {user.role}
        </span>
      </td>
      <td className="px-4 py-3">{user.subscription_plan ?? 'free'}</td>
      <td className="px-4 py-3">{new Date(user.created_at).toLocaleDateString()}</td>
      <td className="px-4 py-3">
        <select
          value={selectedRole}
          onChange={(e) => handleChange(e.target.value)}
          className="rounded bg-gray-700 px-2 py-1 text-sm text-white"
          aria-label={`Role for ${user.clerk_user_id}`}
        >
          <option value="member">member</option>
          <option value="admin">admin</option>
        </select>
      </td>
    </tr>
  );
}
