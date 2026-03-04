'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ItemList } from '@/components/items/item-list';
import { useItems, useDeleteItem } from '@/hooks/use-items';

export default function ItemsPage() {
  const router = useRouter();
  const { data, isLoading, error } = useItems();
  const deleteItem = useDeleteItem();

  function handleEdit(id: string) {
    router.push(`/items/${id}`);
  }

  async function handleDelete(id: string) {
    if (window.confirm('Are you sure you want to delete this item?')) {
      try {
        await deleteItem.mutateAsync(id);
      } catch {
        // React Query tracks error via deleteItem.error
      }
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Items</h1>
        <Button onClick={() => router.push('/items/new')}>New Item</Button>
      </div>

      {deleteItem.error && (
        <div className="mt-4 rounded-lg border border-red-500/50 bg-red-900/20 p-4">
          <p className="text-red-400">Delete failed. Please try again.</p>
        </div>
      )}

      <div className="mt-6">
        {error ? (
          <div className="rounded-lg border border-red-500/50 bg-red-900/20 p-4">
            <p className="text-red-400">Error loading items. Please try again.</p>
          </div>
        ) : (
          <ItemList
            items={data?.items || []}
            isLoading={isLoading}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        )}
      </div>
    </div>
  );
}
