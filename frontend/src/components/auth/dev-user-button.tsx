'use client';

/**
 * Simple "D" avatar circle shown in dev mode instead of Clerk's UserButton.
 */
export function DevUserButton() {
  return (
    <div
      title="Dev Mode"
      className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white"
    >
      D
    </div>
  );
}
