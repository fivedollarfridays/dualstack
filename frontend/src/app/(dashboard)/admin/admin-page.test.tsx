/**
 * Tests for admin dashboard page.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import AdminDashboardPage from './page';

const mockUseAdminHealth = jest.fn();
jest.mock('@/hooks/use-admin', () => ({
  useAdminHealth: () => mockUseAdminHealth(),
}));

describe('AdminDashboardPage', () => {
  it('renders the page heading', () => {
    mockUseAdminHealth.mockReturnValue({ isLoading: true });
    render(<AdminDashboardPage />);
    expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
  });

  it('shows health data when loaded', () => {
    mockUseAdminHealth.mockReturnValue({
      isLoading: false,
      data: { status: 'healthy', user_count: 42, database: 'connected' },
    });
    render(<AdminDashboardPage />);
    expect(screen.getByText('healthy')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    mockUseAdminHealth.mockReturnValue({ isLoading: true });
    render(<AdminDashboardPage />);
    const loadingDots = screen.getAllByText('...');
    expect(loadingDots.length).toBeGreaterThan(0);
  });

  it('renders navigation links to admin sub-pages', () => {
    mockUseAdminHealth.mockReturnValue({
      isLoading: false,
      data: { status: 'healthy', user_count: 10, database: 'connected' },
    });
    render(<AdminDashboardPage />);
    expect(screen.getByText('View Details')).toBeInTheDocument();
    expect(screen.getByText('Manage Users')).toBeInTheDocument();
    expect(screen.getByText('View Logs')).toBeInTheDocument();
  });
});
