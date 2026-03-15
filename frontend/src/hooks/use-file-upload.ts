import { useState, useCallback } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAppAuth } from '@/contexts/auth-context';
import * as api from '@/lib/api/files';

export function useFiles(page = 1, limit = 20) {
  const { getToken } = useAppAuth();
  return useQuery({
    queryKey: ['files', page, limit],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.listFiles(token, page, limit);
    },
  });
}

export function useFileUpload() {
  const { getToken } = useAppAuth();
  const queryClient = useQueryClient();
  const [progress, setProgress] = useState(0);

  const reset = useCallback(() => setProgress(0), []);

  const mutation = useMutation({
    mutationFn: async (file: File) => {
      setProgress(0);
      const token = await getToken();
      if (!token) throw new Error('Authentication required');

      const { upload_url } = await api.requestUploadUrl(
        token, file.name, file.type, file.size
      );

      await api.uploadFileToStorage(upload_url, file, setProgress);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] });
    },
  });

  return { ...mutation, progress, reset };
}

export function useDeleteFile() {
  const { getToken } = useAppAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (fileId: string) => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.deleteFile(token, fileId);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['files'] }),
  });
}
