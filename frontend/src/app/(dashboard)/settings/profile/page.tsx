'use client';

import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { useAppAuth } from '@/contexts/auth-context';
import { AvatarDisplay } from '@/components/profile/avatar-display';
import { ProfileForm } from '@/components/profile/profile-form';
import { DeleteAccountDialog } from '@/components/profile/delete-account-dialog';
import * as api from '@/lib/api/profile';

export default function ProfilePage() {
  const router = useRouter();
  const { getToken } = useAppAuth();
  const queryClient = useQueryClient();

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.getProfile(token);
    },
  });

  const updateMutation = useMutation({
    mutationFn: async (displayName: string) => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.updateProfile(token, { display_name: displayName });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      toast.success('Profile saved');
    },
    onError: () => {
      toast.error('Failed to save profile');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');
      return api.deleteAccount(token);
    },
    onSuccess: () => {
      router.push('/');
    },
    onError: () => {
      toast.error('Failed to delete account');
    },
  });

  if (isLoading) return <p className="text-gray-400">Loading profile...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-white">Profile</h1>
      <p className="mt-2 text-gray-400">Manage your account information.</p>

      <div className="mt-8 flex items-center gap-6">
        <AvatarDisplay
          avatarUrl={profile?.avatar_url ?? null}
          displayName={profile?.display_name ?? null}
        />
        <div>
          <p className="text-lg font-medium text-white">{profile?.display_name ?? 'No name set'}</p>
          <p className="text-sm text-gray-400">{profile?.clerk_user_id}</p>
        </div>
      </div>

      <div className="mt-8 max-w-md">
        <ProfileForm
          displayName={profile?.display_name ?? ''}
          onSave={(name) => updateMutation.mutate(name)}
          isSaving={updateMutation.isPending}
        />
      </div>

      <div className="mt-12 border-t border-gray-700 pt-8">
        <h2 className="text-lg font-bold text-red-400">Danger Zone</h2>
        <p className="mt-2 text-sm text-gray-400">
          Once you delete your account, there is no going back.
        </p>
        <div className="mt-4">
          <DeleteAccountDialog
            onConfirm={() => deleteMutation.mutate()}
            isDeleting={deleteMutation.isPending}
          />
        </div>
      </div>
    </div>
  );
}
