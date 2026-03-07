'use client';

import { UserButton } from '@clerk/nextjs';
import { isClerkEnabled } from '@/lib/auth-config';
import { DevUserButton } from './dev-user-button';

/**
 * Renders Clerk's UserButton when Clerk is enabled, otherwise DevUserButton.
 */
export function AppUserButton() {
  if (isClerkEnabled()) {
    return <UserButton afterSignOutUrl="/" />;
  }
  return <DevUserButton />;
}
