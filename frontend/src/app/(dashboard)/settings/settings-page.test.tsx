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

  it('renders the Profile section', () => {
    render(<SettingsPage />);
    expect(screen.getByText('Profile')).toBeInTheDocument();
    expect(
      screen.getByText(/Update your profile information/)
    ).toBeInTheDocument();
  });

  it('renders the Billing section', () => {
    render(<SettingsPage />);
    expect(screen.getByText('Billing')).toBeInTheDocument();
    expect(
      screen.getByText(/Manage your subscription/)
    ).toBeInTheDocument();
  });

  it('renders the Danger Zone section', () => {
    render(<SettingsPage />);
    expect(screen.getByText('Danger Zone')).toBeInTheDocument();
    expect(
      screen.getByText(/Irreversible actions/)
    ).toBeInTheDocument();
  });
});
