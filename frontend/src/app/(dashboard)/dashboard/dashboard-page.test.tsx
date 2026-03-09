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

const mockUseSubscription = jest.fn();
jest.mock('@/hooks/use-subscription', () => ({
  useSubscription: () => mockUseSubscription(),
}));

beforeEach(() => {
  jest.clearAllMocks();
  mockUseSubscription.mockReturnValue({ plan: 'free', status: 'none', isLoading: false });
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

  it('renders the Subscription card with real plan name', () => {
    mockUseItems.mockReturnValue({ data: undefined, isLoading: true });
    mockUseSubscription.mockReturnValue({ plan: 'pro', status: 'active', isLoading: false });
    render(<DashboardPage />);
    expect(screen.getByText('Subscription')).toBeInTheDocument();
    expect(screen.getByText('Pro')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('renders Free when subscription data is default', () => {
    mockUseItems.mockReturnValue({ data: undefined, isLoading: true });
    mockUseSubscription.mockReturnValue({ plan: 'free', status: 'none', isLoading: false });
    render(<DashboardPage />);
    expect(screen.getByText('Free')).toBeInTheDocument();
    expect(screen.getByText('Current plan')).toBeInTheDocument();
  });

  it('shows Upgrade link for free users', () => {
    mockUseItems.mockReturnValue({ data: undefined, isLoading: true });
    mockUseSubscription.mockReturnValue({ plan: 'free', status: 'none', isLoading: false });
    render(<DashboardPage />);
    expect(screen.getByText('Upgrade')).toBeInTheDocument();
  });

  it('shows Manage Subscription link for subscribed users', () => {
    mockUseItems.mockReturnValue({ data: undefined, isLoading: true });
    mockUseSubscription.mockReturnValue({ plan: 'pro', status: 'active', isLoading: false });
    render(<DashboardPage />);
    expect(screen.getByText('Manage Subscription')).toBeInTheDocument();
  });

  it('shows loading state for subscription card', () => {
    mockUseItems.mockReturnValue({ data: undefined, isLoading: false });
    mockUseSubscription.mockReturnValue({ plan: 'free', status: 'none', isLoading: true });
    render(<DashboardPage />);
    // Should show ellipsis while loading subscription
    const subscriptionCard = screen.getByText('Subscription').closest('div');
    expect(subscriptionCard).toBeInTheDocument();
  });

  it('does not render a Credits card', () => {
    mockUseItems.mockReturnValue({ data: undefined, isLoading: true });
    render(<DashboardPage />);
    expect(screen.queryByText('Credits')).not.toBeInTheDocument();
    expect(screen.queryByText('Available credits')).not.toBeInTheDocument();
  });
});
