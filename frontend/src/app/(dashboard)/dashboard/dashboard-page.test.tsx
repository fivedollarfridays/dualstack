/**
 * Tests for app/(dashboard)/dashboard/page.tsx — Dashboard overview page
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import DashboardPage from './page';

describe('DashboardPage', () => {
  it('renders the page heading', () => {
    render(<DashboardPage />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('renders the welcome message', () => {
    render(<DashboardPage />);
    expect(
      screen.getByText('Welcome to your DualStack dashboard.')
    ).toBeInTheDocument();
  });

  it('renders the Items card', () => {
    render(<DashboardPage />);
    expect(screen.getByText('Items')).toBeInTheDocument();
    expect(screen.getByText('Total items created')).toBeInTheDocument();
  });

  it('renders the Subscription card', () => {
    render(<DashboardPage />);
    expect(screen.getByText('Subscription')).toBeInTheDocument();
    expect(screen.getByText('Free')).toBeInTheDocument();
    expect(screen.getByText('Current plan')).toBeInTheDocument();
  });

  it('renders the Credits card', () => {
    render(<DashboardPage />);
    expect(screen.getByText('Credits')).toBeInTheDocument();
    expect(screen.getByText('Available credits')).toBeInTheDocument();
  });
});
