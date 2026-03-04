'use client';

import { useRouter, useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@clerk/nextjs';
import { Button } from '@/components/ui/button';
import { ItemForm } from '@/components/items/item-form';
import { useUpdateItem, useDeleteItem } from '@/hooks/use-items';
import { getItem } from '@/lib/api/items';

export default function EditItemPage() {
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;
  const { getToken } = useAuth();
  const updateItem = useUpdateItem();
  const deleteItemMutation = useDeleteItem();

  const { data: item, isLoading, error } = useQuery({
    queryKey: ['items', id],
    queryFn: async () => {
      const token = await getToken();
      return getItem(token!, id);
    },
  });

  async function handleSubmit(data: {
    title: string;
    description: string;
    status: 'draft' | 'active' | 'archived';
  }) {
    await updateItem.mutateAsync({ id, data });
    router.push('/items');
  }

  function handleDelete() {
    if (window.confirm('Are you sure you want to delete this item?')) {
      deleteItemMutation.mutate(id);
      router.push('/items');
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-gray-400">Loading item...</p>
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className="rounded-lg border border-red-500/50 bg-red-900/20 p-4">
        <p className="text-red-400">Error loading item. Please try again.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Edit Item</h1>
        <div className="flex gap-2">
          <Button variant="ghost" onClick={() => router.push('/items')}>
            Back
          </Button>
          <Button
            variant="outline"
            onClick={handleDelete}
            className="border-red-600 text-red-400 hover:bg-red-900/20"
          >
            Delete
          </Button>
        </div>
      </div>

      <div className="mt-6 max-w-lg">
        <ItemForm
          onSubmit={handleSubmit}
          initialData={{
            title: item.title,
            description: item.description || '',
            status: item.status,
          }}
          isLoading={updateItem.isPending}
        />
      </div>
    </div>
  );
}
