'use client';

import { Button } from '@/components/ui/button';
import type { ItemResponse } from '@/lib/api/items';

interface ItemCardProps {
  item: ItemResponse;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

const statusStyles: Record<string, string> = {
  draft: 'bg-gray-600 text-gray-200',
  active: 'bg-green-600 text-green-100',
  archived: 'bg-yellow-600 text-yellow-100',
};

export function ItemCard({ item, onEdit, onDelete }: ItemCardProps) {
  return (
    <div className="rounded-lg border border-gray-700 bg-gray-800 p-4">
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-medium text-white truncate">{item.title}</h3>
          {item.description && (
            <p className="mt-1 text-sm text-gray-400 line-clamp-2">
              {item.description}
            </p>
          )}
        </div>
        <span
          className={`ml-2 inline-flex rounded-full px-2 py-1 text-xs font-medium ${statusStyles[item.status]}`}
        >
          {item.status}
        </span>
      </div>
      <div className="mt-4 flex gap-2">
        <Button variant="secondary" size="sm" onClick={() => onEdit(item.id)}>
          Edit
        </Button>
        <Button variant="ghost" size="sm" onClick={() => onDelete(item.id)}>
          Delete
        </Button>
      </div>
    </div>
  );
}
