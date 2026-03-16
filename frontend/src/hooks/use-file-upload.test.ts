/**
 * Tests for useFiles, useFileUpload, and useDeleteFile hooks.
 */
import { renderHook, waitFor, act } from '@testing-library/react';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock auth context
const mockGetToken = jest.fn();
jest.mock('@/contexts/auth-context', () => ({
  useAppAuth: () => ({ getToken: mockGetToken }),
}));

// Mock API module
const mockListFiles = jest.fn();
const mockRequestUploadUrl = jest.fn();
const mockUploadFileToStorage = jest.fn();
const mockDeleteFile = jest.fn();
jest.mock('@/lib/api/files', () => ({
  listFiles: (...args: unknown[]) => mockListFiles(...args),
  requestUploadUrl: (...args: unknown[]) => mockRequestUploadUrl(...args),
  uploadFileToStorage: (...args: unknown[]) => mockUploadFileToStorage(...args),
  deleteFile: (...args: unknown[]) => mockDeleteFile(...args),
}));

import { useFiles, useFileUpload, useDeleteFile } from './use-file-upload';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(QueryClientProvider, { client: queryClient }, children);
  };
}

beforeEach(() => {
  mockGetToken.mockReset();
  mockListFiles.mockReset();
  mockRequestUploadUrl.mockReset();
  mockUploadFileToStorage.mockReset();
  mockDeleteFile.mockReset();
});

describe('useFiles', () => {
  it('fetches files with token', async () => {
    mockGetToken.mockResolvedValue('tok-123');
    mockListFiles.mockResolvedValue({ files: [], total: 0 });

    const { result } = renderHook(() => useFiles(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockListFiles).toHaveBeenCalledWith('tok-123', 1, 20);
  });

  it('passes page and limit parameters', async () => {
    mockGetToken.mockResolvedValue('tok-123');
    mockListFiles.mockResolvedValue({ files: [], total: 0 });

    const { result } = renderHook(() => useFiles(2, 10), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockListFiles).toHaveBeenCalledWith('tok-123', 2, 10);
  });

  it('throws when no token available', async () => {
    mockGetToken.mockResolvedValue(null);

    const { result } = renderHook(() => useFiles(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toBe('Authentication required');
  });
});

describe('useFileUpload', () => {
  it('uploads file using presigned URL flow', async () => {
    mockGetToken.mockResolvedValue('tok-upload');
    mockRequestUploadUrl.mockResolvedValue({
      file_id: 'f1',
      upload_url: 'https://storage/upload',
    });
    mockUploadFileToStorage.mockResolvedValue(undefined);

    const { result } = renderHook(() => useFileUpload(), { wrapper: createWrapper() });

    const file = new File(['data'], 'test.txt', { type: 'text/plain' });

    await act(async () => {
      result.current.mutate(file);
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockRequestUploadUrl).toHaveBeenCalledWith('tok-upload', 'test.txt', 'text/plain', 4);
    expect(mockUploadFileToStorage).toHaveBeenCalledWith(
      'https://storage/upload',
      file,
      expect.any(Function)
    );
  });

  it('throws when no token available', async () => {
    mockGetToken.mockResolvedValue(null);

    const { result } = renderHook(() => useFileUpload(), { wrapper: createWrapper() });

    const file = new File(['data'], 'test.txt', { type: 'text/plain' });

    await act(async () => {
      result.current.mutate(file);
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toBe('Authentication required');
  });

  it('resets progress to zero via reset()', async () => {
    const { result } = renderHook(() => useFileUpload(), { wrapper: createWrapper() });

    act(() => {
      result.current.reset();
    });

    expect(result.current.progress).toBe(0);
  });
});

describe('useDeleteFile', () => {
  it('deletes file with token', async () => {
    mockGetToken.mockResolvedValue('tok-del');
    mockDeleteFile.mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteFile(), { wrapper: createWrapper() });

    await act(async () => {
      result.current.mutate('file-42');
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockDeleteFile).toHaveBeenCalledWith('tok-del', 'file-42');
  });

  it('throws when no token available', async () => {
    mockGetToken.mockResolvedValue(null);

    const { result } = renderHook(() => useDeleteFile(), { wrapper: createWrapper() });

    await act(async () => {
      result.current.mutate('file-42');
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error?.message).toBe('Authentication required');
  });
});
