export default function SettingsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-white">Settings</h1>
      <p className="mt-2 text-gray-400">Manage your account settings.</p>

      <div className="mt-8 max-w-2xl space-y-6">
        {/* Profile section */}
        <div className="rounded-lg border border-gray-700 bg-gray-800 p-6">
          <h2 className="text-lg font-semibold text-white">Profile</h2>
          <p className="mt-1 text-sm text-gray-400">
            Update your profile information. Manage your account through Clerk.
          </p>
        </div>

        {/* Billing section */}
        <div className="rounded-lg border border-gray-700 bg-gray-800 p-6">
          <h2 className="text-lg font-semibold text-white">Billing</h2>
          <p className="mt-1 text-sm text-gray-400">
            Manage your subscription and payment methods.
          </p>
        </div>

        {/* Danger zone */}
        <div className="rounded-lg border border-red-900/50 bg-red-900/10 p-6">
          <h2 className="text-lg font-semibold text-red-400">Danger Zone</h2>
          <p className="mt-1 text-sm text-gray-400">
            Irreversible actions for your account.
          </p>
        </div>
      </div>
    </div>
  );
}
