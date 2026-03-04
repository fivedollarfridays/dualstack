import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@clerk/nextjs';
import * as api from '@/lib/api/items';

export function useItems(page = 1, limit = 20) {
  const { getToken } = useAuth();
  return useQuery({
    queryKey: ['items', page, limit],
    queryFn: async () => {
      const token = await getToken();
      return api.listItems(token!, page, limit);
    },
  });
}

export function useCreateItem() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: api.CreateItemData) => {
      const token = await getToken();
      return api.createItem(token!, data);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['items'] }),
  });
}

export function useUpdateItem() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: api.UpdateItemData }) => {
      const token = await getToken();
      return api.updateItem(token!, id, data);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['items'] }),
  });
}

export function useDeleteItem() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const token = await getToken();
      return api.deleteItem(token!, id);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['items'] }),
  });
}
