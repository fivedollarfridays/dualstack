import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAppAuth } from '@/contexts/auth-context';
import * as api from '@/lib/api/items';

export function useItems(page = 1, limit = 20) {
  const { getToken } = useAppAuth();
  return useQuery({
    queryKey: ['items', page, limit],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.listItems(token, page, limit);
    },
  });
}

export function useCreateItem() {
  const { getToken } = useAppAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: api.CreateItemData) => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.createItem(token, data);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['items'] }),
  });
}

export function useUpdateItem() {
  const { getToken } = useAppAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: api.UpdateItemData }) => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.updateItem(token, id, data);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['items'] }),
  });
}

export function useDeleteItem() {
  const { getToken } = useAppAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.deleteItem(token, id);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['items'] }),
  });
}
