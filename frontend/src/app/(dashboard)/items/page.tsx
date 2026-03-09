'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';
import { ItemList } from '@/components/items/item-list';
import { SearchBar } from '@/components/items/search-bar';
import { SortControls } from '@/components/items/sort-controls';
import type { SortField, SortDir } from '@/components/items/sort-controls';
import { useItems, useDeleteItem } from '@/hooks/use-items';

const PAGE_SIZE = 20;

export default function ItemsPage() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<SortField>('created_at');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const { data, isLoading, error } = useItems(page, PAGE_SIZE, {
    search: search || undefined,
    sort_by: sortBy,
    sort_dir: sortDir,
  });
  const deleteItem = useDeleteItem();

  const handleSearchChange = useCallback((value: string) => {
    setSearch(value);
    setPage(1);
  }, []);

  const handleSortChange = useCallback((field: SortField, dir: SortDir) => {
    setSortBy(field);
    setSortDir(dir);
    setPage(1);
  }, []);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  // Reset to last valid page if items were deleted past current page
  useEffect(() => {
    if (data && page > totalPages) {
      setPage(totalPages);
    }
  }, [data, page, totalPages]);

  function handleEdit(id: string) {
    router.push(`/items/${id}`);
  }

  function handleDelete(id: string) {
    setDeleteTarget(id);
  }

  async function confirmDelete() {
    try {
      await deleteItem.mutateAsync(deleteTarget!);
    } catch {
      // React Query tracks error via deleteItem.error
    }
    setDeleteTarget(null);
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

      <div className="mt-4 flex flex-wrap items-center gap-4">
        <SearchBar value={search} onChange={handleSearchChange} placeholder="Search items..." />
        <SortControls sortBy={sortBy} sortDir={sortDir} onSortChange={handleSortChange} />
      </div>

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

      {/* Pagination */}
      <div className="mt-6 flex items-center justify-between">
        <Button
          variant="outline"
          disabled={page <= 1}
          onClick={() => setPage((p) => p - 1)}
        >
          Previous
        </Button>
        <span className="text-sm text-gray-400">Page {page}</span>
        <Button
          variant="outline"
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
        >
          Next
        </Button>
      </div>

      <ConfirmDialog
        open={deleteTarget !== null}
        title="Delete Item"
        message="Are you sure you want to delete this item? This action cannot be undone."
        confirmLabel="Delete"
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
