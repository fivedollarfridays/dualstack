'use client';

interface UploadProgressProps {
  filename: string;
  percent: number;
}

export function UploadProgress({ filename, percent }: UploadProgressProps) {
  return (
    <div className="rounded bg-gray-800 p-3">
      <div className="flex items-center justify-between text-sm">
        <span className="truncate text-white">{filename}</span>
        <span className="ml-2 text-gray-400">{percent}%</span>
      </div>
      <div className="mt-2 h-2 rounded-full bg-gray-700">
        <div
          className="h-2 rounded-full bg-blue-500 transition-all"
          style={{ width: `${percent}%` }}
          role="progressbar"
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}
