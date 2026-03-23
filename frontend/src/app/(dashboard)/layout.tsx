'use client';

import { useState } from 'react';
import Link from 'next/link';
import { AppUserButton } from '@/components/auth/app-user-button';
import { ErrorBoundary } from '@/components/error-boundary';

const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/items', label: 'Items' },
  { href: '/billing', label: 'Billing' },
  { href: '/settings', label: 'Settings' },
];

const navLinkClassName = 'block rounded-lg px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition-colors';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

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
              className={navLinkClassName}
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
          <div className="md:hidden flex items-center gap-3">
            <button
              type="button"
              aria-label="Menu"
              onClick={() => setMobileNavOpen(!mobileNavOpen)}
              className="rounded-lg p-2 text-gray-300 hover:bg-gray-700 hover:text-white"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <Link href="/dashboard" className="text-lg font-bold text-white">
              DualStack
            </Link>
          </div>
          <div className="hidden md:block" />
          <AppUserButton />
        </header>

        {/* Mobile navigation */}
        <nav
          data-testid="mobile-nav"
          className={`${mobileNavOpen ? '' : 'hidden'} border-b border-gray-700 bg-gray-800 px-3 py-2 md:hidden`}
        >
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={navLinkClassName}
              onClick={() => setMobileNavOpen(false)}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Page content */}
        <main className="flex-1 p-6">
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
