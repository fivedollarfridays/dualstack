export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-white">Dashboard</h1>
      <p className="mt-2 text-gray-400">Welcome to your DualStack dashboard.</p>

      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {/* Items card */}
        <div className="rounded-lg border border-gray-700 bg-gray-800 p-6">
          <h3 className="text-sm font-medium text-gray-400">Items</h3>
          <p className="mt-2 text-3xl font-bold text-white">--</p>
          <p className="mt-1 text-sm text-gray-500">Total items created</p>
        </div>

        {/* Subscription card */}
        <div className="rounded-lg border border-gray-700 bg-gray-800 p-6">
          <h3 className="text-sm font-medium text-gray-400">Subscription</h3>
          <p className="mt-2 text-3xl font-bold text-white">Free</p>
          <p className="mt-1 text-sm text-gray-500">Current plan</p>
        </div>

        {/* Credits card */}
        <div className="rounded-lg border border-gray-700 bg-gray-800 p-6">
          <h3 className="text-sm font-medium text-gray-400">Credits</h3>
          <p className="mt-2 text-3xl font-bold text-white">--</p>
          <p className="mt-1 text-sm text-gray-500">Available credits</p>
        </div>
      </div>
    </div>
  );
}
