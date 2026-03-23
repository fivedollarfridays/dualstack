/**
 * Tests for app/(dashboard)/layout.tsx — Dashboard layout with sidebar, mobile nav
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DashboardLayout from './layout';


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

  it('renders navigation items in sidebar and mobile nav', () => {
    render(
      <DashboardLayout>
        <div>content</div>
      </DashboardLayout>
    );
    // Each nav item appears twice (sidebar + mobile nav)
    expect(screen.getAllByText('Dashboard')).toHaveLength(2);
    expect(screen.getAllByText('Items')).toHaveLength(2);
    expect(screen.getAllByText('Billing')).toHaveLength(2);
    expect(screen.getAllByText('Settings')).toHaveLength(2);
  });

  it('renders navigation links with correct hrefs', () => {
    render(
      <DashboardLayout>
        <div>content</div>
      </DashboardLayout>
    );
    const dashboardLinks = screen.getAllByRole('link', { name: 'Dashboard' });
    expect(dashboardLinks[0]).toHaveAttribute('href', '/dashboard');
    const itemsLinks = screen.getAllByRole('link', { name: 'Items' });
    expect(itemsLinks[0]).toHaveAttribute('href', '/items');
    const billingLinks = screen.getAllByRole('link', { name: 'Billing' });
    expect(billingLinks[0]).toHaveAttribute('href', '/billing');
    const settingsLinks = screen.getAllByRole('link', { name: 'Settings' });
    expect(settingsLinks[0]).toHaveAttribute('href', '/settings');
  });

  it('renders a mobile menu button', () => {
    render(
      <DashboardLayout>
        <div>content</div>
      </DashboardLayout>
    );
    expect(screen.getByRole('button', { name: /menu/i })).toBeInTheDocument();
  });

  it('toggles mobile navigation when menu button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <DashboardLayout>
        <div>content</div>
      </DashboardLayout>
    );

    // Mobile nav should be hidden initially
    const mobileNav = screen.getByTestId('mobile-nav');
    expect(mobileNav).toHaveClass('hidden');

    // Click menu button to open
    await user.click(screen.getByRole('button', { name: /menu/i }));
    expect(mobileNav).not.toHaveClass('hidden');

    // Click again to close
    await user.click(screen.getByRole('button', { name: /menu/i }));
    expect(mobileNav).toHaveClass('hidden');
  });

  it('closes mobile nav when a nav link is clicked', async () => {
    const user = userEvent.setup();
    render(
      <DashboardLayout>
        <div>content</div>
      </DashboardLayout>
    );

    const mobileNav = screen.getByTestId('mobile-nav');

    // Open mobile nav
    await user.click(screen.getByRole('button', { name: /menu/i }));
    expect(mobileNav).not.toHaveClass('hidden');

    // Click a nav link inside mobile nav
    const mobileLinks = mobileNav.querySelectorAll('a');
    await user.click(mobileLinks[0]);
    expect(mobileNav).toHaveClass('hidden');
  });
});

describe('DashboardLayout ErrorBoundary', () => {
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('catches child render errors and shows fallback', () => {
    function BrokenChild(): JSX.Element {
      throw new Error('Page crash');
    }

    render(
      <DashboardLayout>
        <BrokenChild />
      </DashboardLayout>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
  });

  it('renders page content normally when no error occurs', () => {
    render(
      <DashboardLayout>
        <div>Dashboard page</div>
      </DashboardLayout>
    );

    expect(screen.getByText('Dashboard page')).toBeInTheDocument();
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
  });
});
