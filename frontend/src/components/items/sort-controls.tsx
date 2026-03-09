'use client';

import type { SortField, SortDir } from '@/lib/api/items';
export type { SortField, SortDir };

interface SortControlsProps {
  sortBy: SortField;
  sortDir: SortDir;
  onSortChange: (field: SortField, dir: SortDir) => void;
}

const SORT_OPTIONS: { value: SortField; label: string }[] = [
  { value: 'created_at', label: 'Created' },
  { value: 'updated_at', label: 'Updated' },
  { value: 'title', label: 'Title' },
];

export function SortControls({ sortBy, sortDir, onSortChange }: SortControlsProps) {
  return (
    <div className="flex items-center gap-2">
      <select
        value={sortBy}
        onChange={(e) => onSortChange(e.target.value as SortField, sortDir)}
        className="rounded bg-gray-700 px-3 py-2 text-sm text-white"
        aria-label="Sort by"
      >
        {SORT_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      <button
        onClick={() => onSortChange(sortBy, sortDir === 'asc' ? 'desc' : 'asc')}
        className="rounded bg-gray-700 px-3 py-2 text-sm text-white"
        aria-label={`Sort ${sortDir === 'asc' ? 'descending' : 'ascending'}`}
      >
        {sortDir === 'asc' ? '\u2191' : '\u2193'}
      </button>
    </div>
  );
}
