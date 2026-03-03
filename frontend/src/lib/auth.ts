import { auth, currentUser } from '@clerk/nextjs/server';

/**
 * Get the current user's ID from the server
 * Returns null if not authenticated
 */
export async function getCurrentUserId(): Promise<string | null> {
  const { userId } = await auth();
  return userId;
}

/**
 * Get the current user's full profile from the server
 * Returns null if not authenticated
 */
export async function getCurrentUser() {
  const user = await currentUser();
  return user;
}

/**
 * Check if the current user is authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
  const { userId } = await auth();
  return !!userId;
}
