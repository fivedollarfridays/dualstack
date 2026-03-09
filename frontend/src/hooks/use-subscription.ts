import { useQuery } from '@tanstack/react-query';
import { useAppAuth } from '@/contexts/auth-context';
import { getSubscription } from '@/lib/api/billing';

export function useSubscription() {
  const { getToken } = useAppAuth();
  const query = useQuery({
    queryKey: ['subscription'],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return getSubscription(token);
    },
    staleTime: 5 * 60 * 1000,
  });

  return {
    plan: query.data?.subscription_plan ?? 'free',
    status: query.data?.subscription_status ?? 'none',
    isLoading: query.isLoading,
  };
}
