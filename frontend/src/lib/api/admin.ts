import { API_URL, authHeaders, handleResponse } from './shared';

export interface AdminUser {
  id: string;
  clerk_user_id: string;
  role: string;
  subscription_plan: string | null;
  subscription_status: string | null;
  created_at: string;
  updated_at: string;
}

export interface AdminUserListResponse {
  users: AdminUser[];
  total: number;
}

export interface HealthResponse {
  status: string;
  database: string;
  user_count: number;
}

export interface AuditEntry {
  id: string;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  outcome: string;
  detail: string;
  created_at: string;
}

export interface AuditLogResponse {
  entries: AuditEntry[];
  total: number;
}

export async function listUsers(
  token: string,
  page = 1,
  limit = 20,
  search?: string
): Promise<AdminUserListResponse> {
  const params = new URLSearchParams({ page: String(page), limit: String(limit) });
  if (search) params.set('search', search);
  const response = await fetch(`${API_URL}/api/v1/admin/users?${params}`, {
    headers: authHeaders(token),
  });
  return handleResponse<AdminUserListResponse>(response);
}

export async function updateUserRole(
  token: string,
  userId: string,
  role: string
): Promise<AdminUser> {
  const response = await fetch(`${API_URL}/api/v1/admin/users/${userId}/role`, {
    method: 'PATCH',
    headers: authHeaders(token),
    body: JSON.stringify({ role }),
  });
  return handleResponse<AdminUser>(response);
}

export async function getHealth(token: string): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/api/v1/admin/health`, {
    headers: authHeaders(token),
  });
  return handleResponse<HealthResponse>(response);
}

export async function listAuditLogs(
  token: string,
  page = 1,
  limit = 50
): Promise<AuditLogResponse> {
  const params = new URLSearchParams({ page: String(page), limit: String(limit) });
  const response = await fetch(`${API_URL}/api/v1/admin/audit?${params}`, {
    headers: authHeaders(token),
  });
  return handleResponse<AuditLogResponse>(response);
}
