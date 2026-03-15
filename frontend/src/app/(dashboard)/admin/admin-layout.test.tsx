/**
 * Tests for admin layout — role gate using admin health endpoint.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import AdminLayout from './layout';

const mockUseAdminHealth = jest.fn();
jest.mock('@/hooks/use-admin', () => ({
  useAdminHealth: () => mockUseAdminHealth(),
}));

describe('AdminLayout', () => {
  it('shows loading state while checking access', () => {
    mockUseAdminHealth.mockReturnValue({ isLoading: true, isError: false });
    render(
      <AdminLayout>
        <div>Admin content</div>
      </AdminLayout>
    );
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(screen.queryByText('Admin content')).not.toBeInTheDocument();
  });

  it('shows access denied for non-admin users (403)', () => {
    mockUseAdminHealth.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new Error('API error: 403 Forbidden'),
    });
    render(
      <AdminLayout>
        <div>Admin content</div>
      </AdminLayout>
    );
    expect(screen.getByText('Access Denied')).toBeInTheDocument();
    expect(screen.queryByText('Admin content')).not.toBeInTheDocument();
  });

  it('shows access denied for Insufficient permissions error', () => {
    mockUseAdminHealth.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new Error('Insufficient permissions'),
    });
    render(
      <AdminLayout>
        <div>Admin content</div>
      </AdminLayout>
    );
    expect(screen.getByText('Access Denied')).toBeInTheDocument();
    expect(screen.queryByText('Admin content')).not.toBeInTheDocument();
  });

  it('shows error message for non-403 errors', () => {
    mockUseAdminHealth.mockReturnValue({
      isLoading: false,
      isError: true,
      error: new Error('Network error'),
    });
    render(
      <AdminLayout>
        <div>Admin content</div>
      </AdminLayout>
    );
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.queryByText('Admin content')).not.toBeInTheDocument();
  });

  it('shows generic error when error has no message', () => {
    mockUseAdminHealth.mockReturnValue({
      isLoading: false,
      isError: true,
      error: { message: undefined },
    });
    render(
      <AdminLayout>
        <div>Admin content</div>
      </AdminLayout>
    );
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.queryByText('Admin content')).not.toBeInTheDocument();
  });

  it('shows generic error when error object is null', () => {
    mockUseAdminHealth.mockReturnValue({
      isLoading: false,
      isError: true,
      error: null,
    });
    render(
      <AdminLayout>
        <div>Admin content</div>
      </AdminLayout>
    );
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('renders children for admin users', () => {
    mockUseAdminHealth.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { status: 'healthy', user_count: 5, database: 'connected' },
    });
    render(
      <AdminLayout>
        <div>Admin content</div>
      </AdminLayout>
    );
    expect(screen.getByText('Admin content')).toBeInTheDocument();
    expect(screen.queryByText('Access Denied')).not.toBeInTheDocument();
  });
});
