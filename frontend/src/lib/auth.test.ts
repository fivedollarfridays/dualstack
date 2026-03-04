/**
 * Tests for lib/auth.ts — server-side Clerk authentication helpers
 */

// Mock @clerk/nextjs/server before importing the module under test
const mockAuth = jest.fn();
const mockCurrentUser = jest.fn();

jest.mock('@clerk/nextjs/server', () => ({
  auth: mockAuth,
  currentUser: mockCurrentUser,
}));

import { getCurrentUserId, getCurrentUser, isAuthenticated } from './auth';

beforeEach(() => {
  jest.clearAllMocks();
});

describe('getCurrentUserId', () => {
  it('returns the user ID when authenticated', async () => {
    mockAuth.mockResolvedValue({ userId: 'user_abc123' });

    const result = await getCurrentUserId();

    expect(result).toBe('user_abc123');
    expect(mockAuth).toHaveBeenCalledTimes(1);
  });

  it('returns null when not authenticated', async () => {
    mockAuth.mockResolvedValue({ userId: null });

    const result = await getCurrentUserId();

    expect(result).toBeNull();
  });
});

describe('getCurrentUser', () => {
  it('returns the user object when authenticated', async () => {
    const mockUserObj = {
      id: 'user_abc123',
      firstName: 'John',
      lastName: 'Doe',
      emailAddresses: [{ emailAddress: 'john@example.com' }],
    };
    mockCurrentUser.mockResolvedValue(mockUserObj);

    const result = await getCurrentUser();

    expect(result).toEqual(mockUserObj);
    expect(mockCurrentUser).toHaveBeenCalledTimes(1);
  });

  it('returns null when not authenticated', async () => {
    mockCurrentUser.mockResolvedValue(null);

    const result = await getCurrentUser();

    expect(result).toBeNull();
  });
});

describe('isAuthenticated', () => {
  it('returns true when user is authenticated', async () => {
    mockAuth.mockResolvedValue({ userId: 'user_abc123' });

    const result = await isAuthenticated();

    expect(result).toBe(true);
  });

  it('returns false when user is not authenticated', async () => {
    mockAuth.mockResolvedValue({ userId: null });

    const result = await isAuthenticated();

    expect(result).toBe(false);
  });
});
