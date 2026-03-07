'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ItemForm } from '@/components/items/item-form';
import { useCreateItem } from '@/hooks/use-items';
import type { ItemStatus } from '@/lib/api/items';

export default function NewItemPage() {
  const router = useRouter();
  const createItem = useCreateItem();

  async function handleSubmit(data: {
    title: string;
    description: string;
    status: ItemStatus;
  }) {
    await createItem.mutateAsync(data);
    router.push('/items');
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">New Item</h1>
        <Button variant="ghost" onClick={() => router.push('/items')}>
          Cancel
        </Button>
      </div>

      <div className="mt-6 max-w-lg">
        <ItemForm onSubmit={handleSubmit} isLoading={createItem.isPending} />
      </div>
    </div>
  );
}
