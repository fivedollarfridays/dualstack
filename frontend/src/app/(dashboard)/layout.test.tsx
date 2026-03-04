/**
 * Tests for app/(dashboard)/layout.tsx — Dashboard layout with sidebar and nav
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import DashboardLayout from './layout';

// Mock next/link to render a plain anchor
jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ href, children, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) =>
    React.createElement('a', { href, ...props }, children),
}));

describe('DashboardLayout', () => {
  it('renders children in the main content area', () => {
    render(
      <DashboardLayout>
        <div>Page content</div>
      </DashboardLayout>
    );
    expect(screen.getByText('Page content')).toBeInTheDocument();
  });

  it('renders the DualStack branding link in sidebar', () => {
    render(
      <DashboardLayout>
        <div>content</div>
      </DashboardLayout>
    );
    const brandLinks = screen.getAllByText('DualStack');
    expect(brandLinks.length).toBeGreaterThanOrEqual(1);
  });

  it('renders navigation items', () => {
    render(
      <DashboardLayout>
        <div>content</div>
      </DashboardLayout>
    );
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Items')).toBeInTheDocument();
    expect(screen.getByText('Billing')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('renders navigation links with correct hrefs', () => {
    render(
      <DashboardLayout>
        <div>content</div>
      </DashboardLayout>
    );
    expect(screen.getByRole('link', { name: 'Dashboard' })).toHaveAttribute(
      'href',
      '/dashboard'
    );
    expect(screen.getByRole('link', { name: 'Items' })).toHaveAttribute(
      'href',
      '/items'
    );
    expect(screen.getByRole('link', { name: 'Billing' })).toHaveAttribute(
      'href',
      '/billing'
    );
    expect(screen.getByRole('link', { name: 'Settings' })).toHaveAttribute(
      'href',
      '/settings'
    );
  });
});
