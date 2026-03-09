'use client';

import { useState } from 'react';
import { CONFIRM_PHRASE } from '@/lib/constants';

interface DeleteAccountDialogProps {
  onConfirm: () => void;
  isDeleting?: boolean;
}

export function DeleteAccountDialog({ onConfirm, isDeleting = false }: DeleteAccountDialogProps) {
  const [open, setOpen] = useState(false);
  const [typed, setTyped] = useState('');

  const isConfirmed = typed === CONFIRM_PHRASE;

  return (
    <div>
      {!open ? (
        <button
          onClick={() => setOpen(true)}
          className="rounded bg-red-700 px-4 py-2 text-sm font-medium text-white hover:bg-red-600"
        >
          Delete Account
        </button>
      ) : (
        <div className="rounded border border-red-700 bg-gray-800 p-4">
          <h3 className="text-lg font-bold text-red-400">Delete Your Account</h3>
          <p className="mt-2 text-sm text-gray-400">
            This action is <strong>permanent and irreversible</strong>. All your data, items, and
            subscription will be deleted.
          </p>
          <p className="mt-3 text-sm text-gray-400">
            Type <code className="text-red-300">{CONFIRM_PHRASE}</code> to confirm:
          </p>
          <input
            type="text"
            value={typed}
            onChange={(e) => setTyped(e.target.value)}
            placeholder={CONFIRM_PHRASE}
            className="mt-2 w-full rounded bg-gray-700 px-4 py-2 text-white"
            aria-label="Confirmation phrase"
          />
          <div className="mt-3 flex gap-3">
            <button
              onClick={onConfirm}
              disabled={!isConfirmed || isDeleting}
              className="rounded bg-red-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {isDeleting ? 'Deleting...' : 'Permanently Delete'}
            </button>
            <button
              onClick={() => { setOpen(false); setTyped(''); }}
              className="rounded bg-gray-700 px-4 py-2 text-sm text-white"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
