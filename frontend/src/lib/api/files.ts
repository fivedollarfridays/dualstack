import { API_URL, authHeaders, handleResponse } from './shared';

export interface FileRecord {
  id: string;
  filename: string;
  size: number;
  content_type: string;
  created_at: string;
}

export interface FileListResponse {
  files: FileRecord[];
  total: number;
}

export interface UploadUrlResponse {
  file_id: string;
  upload_url: string;
}

export interface DownloadUrlResponse {
  download_url: string;
}

export async function requestUploadUrl(
  token: string,
  filename: string,
  contentType: string,
  size: number
): Promise<UploadUrlResponse> {
  const response = await fetch(`${API_URL}/api/v1/files/upload-url`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ filename, content_type: contentType, size }),
  });
  return handleResponse<UploadUrlResponse>(response);
}

export async function listFiles(
  token: string,
  page = 1,
  limit = 20
): Promise<FileListResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/files?page=${page}&limit=${limit}`,
    { headers: authHeaders(token) }
  );
  return handleResponse<FileListResponse>(response);
}

export async function getDownloadUrl(
  token: string,
  fileId: string
): Promise<DownloadUrlResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/files/${fileId}/download-url`,
    { headers: authHeaders(token) }
  );
  return handleResponse<DownloadUrlResponse>(response);
}

export async function deleteFile(
  token: string,
  fileId: string
): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/files/${fileId}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  });
  await handleResponse(response);
}

export async function uploadFileToStorage(
  uploadUrl: string,
  file: File,
  onProgress?: (percent: number) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('PUT', uploadUrl);
    xhr.setRequestHeader('Content-Type', file.type);

    if (onProgress) {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          onProgress(Math.round((e.loaded / e.total) * 100));
        }
      });
    }

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve();
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    });

    xhr.addEventListener('error', () => reject(new Error('Upload failed')));
    xhr.send(file);
  });
}
