import Link from 'next/link';
import { UserButton } from '@clerk/nextjs';

const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/items', label: 'Items' },
  { href: '/billing', label: 'Billing' },
  { href: '/settings', label: 'Settings' },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-gray-900">
      {/* Sidebar */}
      <aside className="hidden w-64 border-r border-gray-700 bg-gray-800 md:block">
        <div className="flex h-16 items-center border-b border-gray-700 px-6">
          <Link href="/dashboard" className="text-lg font-bold text-white">
            DualStack
          </Link>
        </div>
        <nav className="mt-6 space-y-1 px-3">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block rounded-lg px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col">
        {/* Top bar */}
        <header className="flex h-16 items-center justify-between border-b border-gray-700 bg-gray-800 px-6">
          {/* Mobile nav placeholder */}
          <div className="md:hidden">
            <Link href="/dashboard" className="text-lg font-bold text-white">
              DualStack
            </Link>
          </div>
          <div className="hidden md:block" />
          <UserButton afterSignOutUrl="/" />
        </header>

        {/* Page content */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
