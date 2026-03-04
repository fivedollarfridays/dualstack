import { API_URL, authHeaders, handleResponse } from './shared';

export interface ItemResponse {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: 'draft' | 'active' | 'archived';
  created_at: string;
  updated_at: string;
}

export interface ItemListResponse {
  items: ItemResponse[];
  total: number;
}

export interface CreateItemData {
  title: string;
  description?: string;
  status?: 'draft' | 'active' | 'archived';
}

export interface UpdateItemData {
  title?: string;
  description?: string;
  status?: 'draft' | 'active' | 'archived';
}

export async function listItems(
  token: string,
  page = 1,
  limit = 20
): Promise<ItemListResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/items?page=${page}&limit=${limit}`,
    { headers: authHeaders(token) }
  );
  return handleResponse<ItemListResponse>(response);
}

export async function createItem(
  token: string,
  data: CreateItemData
): Promise<ItemResponse> {
  const response = await fetch(`${API_URL}/api/v1/items`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
  return handleResponse<ItemResponse>(response);
}

export async function getItem(
  token: string,
  id: string
): Promise<ItemResponse> {
  const response = await fetch(`${API_URL}/api/v1/items/${id}`, {
    headers: authHeaders(token),
  });
  return handleResponse<ItemResponse>(response);
}

export async function updateItem(
  token: string,
  id: string,
  data: UpdateItemData
): Promise<ItemResponse> {
  const response = await fetch(`${API_URL}/api/v1/items/${id}`, {
    method: 'PATCH',
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
  return handleResponse<ItemResponse>(response);
}

export async function deleteItem(
  token: string,
  id: string
): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/items/${id}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  });
  await handleResponse(response);
}
