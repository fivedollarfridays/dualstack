/**
 * Tests for app/(dashboard)/settings/page.tsx — Settings page
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import SettingsPage from './page';


describe('SettingsPage', () => {
  it('renders the page heading', () => {
    render(<SettingsPage />);
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('renders the description text', () => {
    render(<SettingsPage />);
    expect(
      screen.getByText('Manage your account settings.')
    ).toBeInTheDocument();
  });

  it('renders the Profile section with Manage Account link', () => {
    render(<SettingsPage />);
    expect(screen.getByText('Profile')).toBeInTheDocument();
    const manageLink = screen.getByRole('link', { name: /manage account/i });
    expect(manageLink).toHaveAttribute('href', '/user-profile');
  });

  it('renders the Billing section with link to billing page', () => {
    render(<SettingsPage />);
    expect(screen.getByText('Billing')).toBeInTheDocument();
    const billingLink = screen.getByRole('link', { name: /manage billing/i });
    expect(billingLink).toHaveAttribute('href', '/billing');
  });

  it('does not render a Danger Zone section', () => {
    render(<SettingsPage />);
    expect(screen.queryByText('Danger Zone')).not.toBeInTheDocument();
  });
});
