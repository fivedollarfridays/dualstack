import { CONFIRM_PHRASE } from '@/lib/constants';
import { API_URL, authHeaders, handleResponse } from './shared';

export interface UserProfile {
  clerk_user_id: string;
  display_name: string | null;
  avatar_url: string | null;
  role: string;
  subscription_plan: string | null;
  subscription_status: string | null;
  created_at: string;
}

export interface ProfileUpdateData {
  display_name?: string;
  avatar_url?: string;
}

export async function getProfile(token: string): Promise<UserProfile> {
  const response = await fetch(`${API_URL}/api/v1/users/me/profile`, {
    headers: authHeaders(token),
  });
  return handleResponse<UserProfile>(response);
}

export async function updateProfile(
  token: string,
  data: ProfileUpdateData
): Promise<UserProfile> {
  const response = await fetch(`${API_URL}/api/v1/users/me/profile`, {
    method: 'PATCH',
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
  return handleResponse<UserProfile>(response);
}

export async function deleteAccount(token: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/users/me`, {
    method: 'DELETE',
    headers: {
      ...authHeaders(token),
      'X-Confirm-Delete': CONFIRM_PHRASE,
    },
  });
  await handleResponse(response);
}
