/**
 * Tests for app/(dashboard)/dashboard/page.tsx — Dashboard overview page
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import DashboardPage from './page';

const mockUseItems = jest.fn();
jest.mock('@/hooks/use-items', () => ({
  useItems: (...args: unknown[]) => mockUseItems(...args),
}));

// Dashboard calls useItems(1, 1) to minimize payload — only needs total count

beforeEach(() => {
  jest.clearAllMocks();
});

describe('DashboardPage', () => {
  it('renders the page heading', () => {
    mockUseItems.mockReturnValue({ data: undefined, isLoading: true });
    render(<DashboardPage />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('renders the welcome message', () => {
    mockUseItems.mockReturnValue({ data: undefined, isLoading: true });
    render(<DashboardPage />);
    expect(
      screen.getByText('Welcome to your DualStack dashboard.')
    ).toBeInTheDocument();
  });

  it('shows loading indicator while items are loading', () => {
    mockUseItems.mockReturnValue({ data: undefined, isLoading: true });
    render(<DashboardPage />);
    expect(screen.getByText('…')).toBeInTheDocument();
  });

  it('shows actual item count from API', () => {
    mockUseItems.mockReturnValue({
      data: { items: [], total: 5 },
      isLoading: false,
    });
    render(<DashboardPage />);
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('Total items created')).toBeInTheDocument();
  });

  it('renders the Subscription card', () => {
    mockUseItems.mockReturnValue({ data: undefined, isLoading: true });
    render(<DashboardPage />);
    expect(screen.getByText('Subscription')).toBeInTheDocument();
    expect(screen.getByText('Free')).toBeInTheDocument();
    expect(screen.getByText('Current plan')).toBeInTheDocument();
  });

  it('does not render a Credits card', () => {
    mockUseItems.mockReturnValue({ data: undefined, isLoading: true });
    render(<DashboardPage />);
    expect(screen.queryByText('Credits')).not.toBeInTheDocument();
    expect(screen.queryByText('Available credits')).not.toBeInTheDocument();
  });
});
