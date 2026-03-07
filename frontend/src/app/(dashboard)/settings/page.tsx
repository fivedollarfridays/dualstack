import Link from 'next/link';
import { buttonVariants } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function SettingsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-white">Settings</h1>
      <p className="mt-2 text-gray-400">Manage your account settings.</p>

      <div className="mt-8 max-w-2xl space-y-6">
        {/* Profile section */}
        <Card>
          <h2 className="text-lg font-semibold text-white">Profile</h2>
          <p className="mt-1 text-sm text-gray-400">
            Update your profile information and manage your account through Clerk.
          </p>
          <Link
            href="/user-profile"
            className={buttonVariants({ variant: 'default', className: 'mt-4' })}
          >
            Manage Account
          </Link>
        </Card>

        {/* Billing section */}
        <Card>
          <h2 className="text-lg font-semibold text-white">Billing</h2>
          <p className="mt-1 text-sm text-gray-400">
            Manage your subscription and payment methods.
          </p>
          <Link
            href="/billing"
            className={buttonVariants({ variant: 'secondary', className: 'mt-4' })}
          >
            Manage Billing
          </Link>
        </Card>
      </div>
    </div>
  );
}
