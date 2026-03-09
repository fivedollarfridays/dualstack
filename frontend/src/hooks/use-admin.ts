import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAppAuth } from '@/contexts/auth-context';
import * as api from '@/lib/api/admin';

export function useAdminUsers(page = 1, limit = 20, search?: string) {
  const { getToken } = useAppAuth();
  return useQuery({
    queryKey: ['admin', 'users', page, limit, search],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.listUsers(token, page, limit, search);
    },
  });
}

export function useUpdateUserRole() {
  const { getToken } = useAppAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ userId, role }: { userId: string; role: string }) => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.updateUserRole(token, userId, role);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'users'] }),
  });
}

export function useAdminHealth() {
  const { getToken } = useAppAuth();
  return useQuery({
    queryKey: ['admin', 'health'],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.getHealth(token);
    },
  });
}

export function useAdminAuditLogs(page = 1, limit = 50) {
  const { getToken } = useAppAuth();
  return useQuery({
    queryKey: ['admin', 'audit', page, limit],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.listAuditLogs(token, page, limit);
    },
  });
}
