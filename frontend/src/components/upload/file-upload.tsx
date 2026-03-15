'use client';

import { useCallback, useRef, useState } from 'react';

interface FileUploadProps {
  onUpload: (file: File) => void;
  accept?: string;
  maxSizeMB?: number;
  disabled?: boolean;
}

export function FileUpload({
  onUpload,
  accept,
  maxSizeMB = 100,
  disabled = false,
}: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndUpload = useCallback(
    (file: File) => {
      setError(null);
      const maxBytes = maxSizeMB * 1024 * 1024;
      if (file.size > maxBytes) {
        setError(`File exceeds ${maxSizeMB}MB limit`);
        return;
      }
      onUpload(file);
    },
    [onUpload, maxSizeMB]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragActive(false);
      if (disabled) return;
      const file = e.dataTransfer.files[0];
      if (file) validateAndUpload(file);
    },
    [disabled, validateAndUpload]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) validateAndUpload(file);
    },
    [validateAndUpload]
  );

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        className={`rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
          dragActive ? 'border-blue-500 bg-blue-500/10' : 'border-gray-600 hover:border-gray-400'
        } ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => !disabled && inputRef.current?.click()}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click(); }}
      >
        <p className="text-gray-400">
          {dragActive ? 'Drop file here' : 'Drag and drop a file, or click to browse'}
        </p>
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept={accept}
          onChange={handleChange}
          disabled={disabled}
          data-testid="file-input"
        />
      </div>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
    </div>
  );
}
