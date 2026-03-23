'use client';

import Image from 'next/image';

interface AvatarDisplayProps {
  avatarUrl: string | null;
  displayName: string | null;
  size?: number;
}

export function AvatarDisplay({ avatarUrl, displayName, size = 64 }: AvatarDisplayProps) {
  const initials = displayName
    ? displayName.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : '?';

  if (avatarUrl) {
    return (
      <Image
        src={avatarUrl}
        alt={displayName ?? 'User avatar'}
        width={size}
        height={size}
        className="rounded-full object-cover"
      />
    );
  }

  return (
    <div
      className="flex items-center justify-center rounded-full bg-gray-600 font-bold text-white"
      style={{ width: size, height: size, fontSize: size * 0.4 }}
      aria-label={displayName ?? 'User avatar'}
    >
      {initials}
    </div>
  );
}
