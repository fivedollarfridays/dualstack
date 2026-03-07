'use client';

import { FormEvent, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import type { ItemStatus } from '@/lib/api/items';

interface ItemFormData {
  title: string;
  description: string;
  status: ItemStatus;
}

interface ItemFormProps {
  onSubmit: (data: ItemFormData) => void;
  initialData?: Partial<ItemFormData>;
  isLoading?: boolean;
}

export function ItemForm({ onSubmit, initialData, isLoading }: ItemFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [status, setStatus] = useState<ItemStatus>(
    initialData?.status || 'draft'
  );

  const isEdit = !!initialData;

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    onSubmit({ title, description, status });
  }

  const buttonLabel = isLoading ? 'Saving...' : isEdit ? 'Update' : 'Create';

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="title">Title</Label>
        <Input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter item title"
          required
        />
      </div>

      <div>
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter item description (optional)"
        />
      </div>

      <div>
        <Label htmlFor="status">Status</Label>
        <select
          id="status"
          value={status}
          onChange={(e) => setStatus(e.target.value as ItemStatus)}
          className="flex h-10 w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      <Button type="submit" disabled={isLoading}>
        {buttonLabel}
      </Button>
    </form>
  );
}
