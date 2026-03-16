import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { useAppAuth } from '@/contexts/auth-context';
import * as api from '@/lib/api/items';

export function useItems(
  page = 1,
  limit = 20,
  params?: Omit<api.ListItemsParams, 'page' | 'limit'>
) {
  const { getToken } = useAppAuth();
  return useQuery({
    queryKey: ['items', page, limit, params],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.listItems(token, page, limit, params);
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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      toast.success('Item created');
    },
    onError: () => {
      toast.error('Failed to create item');
    },
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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      toast.success('Item updated');
    },
    onError: () => {
      toast.error('Failed to update item');
    },
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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      toast.success('Item deleted');
    },
    onError: () => {
      toast.error('Failed to delete item');
    },
  });
}
