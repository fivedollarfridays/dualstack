'use client';

import { useState } from 'react';

interface ProfileFormProps {
  displayName: string;
  onSave: (displayName: string) => void;
  isSaving?: boolean;
}

export function ProfileForm({ displayName, onSave, isSaving = false }: ProfileFormProps) {
  const [name, setName] = useState(displayName);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(name);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="display-name" className="block text-sm font-medium text-gray-400">
          Display Name
        </label>
        <input
          id="display-name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-1 w-full rounded bg-gray-700 px-4 py-2 text-white"
          maxLength={255}
        />
      </div>
      <button
        type="submit"
        disabled={isSaving}
        className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
      >
        {isSaving ? 'Saving...' : 'Save'}
      </button>
    </form>
  );
}
