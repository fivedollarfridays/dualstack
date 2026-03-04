/**
 * Tests for app/(dashboard)/billing/page.tsx — Billing page
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BillingPage from './page';

// Mock the billing API
const mockCreateCheckout = jest.fn();
const mockOpenPortal = jest.fn();
jest.mock('@/lib/api/billing', () => ({
  createCheckout: (...args: unknown[]) => mockCreateCheckout(...args),
  openPortal: (...args: unknown[]) => mockOpenPortal(...args),
}));

// Override the global clerk mock to include getToken
const mockGetToken = jest.fn();
jest.mock('@clerk/nextjs', () => ({
  useUser: () => ({ user: { id: 'test-user-123' }, isLoaded: true, isSignedIn: true }),
  useAuth: () => ({
    userId: 'test-user-123',
    isLoaded: true,
    isSignedIn: true,
    getToken: mockGetToken,
  }),
  useClerk: () => ({ signOut: jest.fn() }),
  ClerkProvider: ({ children }: { children: React.ReactNode }) => children,
  SignedIn: ({ children }: { children: React.ReactNode }) => children,
  SignedOut: ({ children }: { children: React.ReactNode }) => null,
  UserButton: () => null,
}));

beforeEach(() => {
  jest.clearAllMocks();
  mockGetToken.mockResolvedValue('mock-token');
});

describe('BillingPage', () => {
  it('renders the page heading', () => {
    render(<BillingPage />);
    expect(screen.getByText('Billing')).toBeInTheDocument();
  });

  it('renders Free plan card', () => {
    render(<BillingPage />);
    expect(screen.getByText('Free')).toBeInTheDocument();
    expect(screen.getByText('$0/mo')).toBeInTheDocument();
  });

  it('renders Pro plan card', () => {
    render(<BillingPage />);
    expect(screen.getByText('Pro')).toBeInTheDocument();
    expect(screen.getByText('$10/mo')).toBeInTheDocument();
  });

  it('shows Free plan as current', () => {
    render(<BillingPage />);
    const buttons = screen.getAllByRole('button');
    const currentPlanButton = buttons.find(
      (b) => b.textContent === 'Current Plan'
    );
    expect(currentPlanButton).toBeInTheDocument();
    expect(currentPlanButton).toBeDisabled();
  });

  it('shows Subscribe button for Pro plan', () => {
    render(<BillingPage />);
    expect(
      screen.getByRole('button', { name: /subscribe/i })
    ).toBeInTheDocument();
  });

  it('renders Manage Subscription button', () => {
    render(<BillingPage />);
    expect(
      screen.getByRole('button', { name: /manage subscription/i })
    ).toBeInTheDocument();
  });

  it('calls createCheckout with token and price on Subscribe click', async () => {
    const user = userEvent.setup();
    mockCreateCheckout.mockResolvedValueOnce('https://checkout.stripe.com/session123');

    render(<BillingPage />);
    await user.click(screen.getByRole('button', { name: /subscribe/i }));

    await waitFor(() => {
      expect(mockCreateCheckout).toHaveBeenCalledWith(
        'mock-token',
        'price_pro_monthly'
      );
    });
  });

  it('calls openPortal with token on Manage Subscription click', async () => {
    const user = userEvent.setup();
    mockOpenPortal.mockResolvedValueOnce('https://billing.stripe.com/portal123');

    render(<BillingPage />);
    await user.click(
      screen.getByRole('button', { name: /manage subscription/i })
    );

    await waitFor(() => {
      expect(mockOpenPortal).toHaveBeenCalledWith('mock-token');
    });
  });

  it('does not call createCheckout if getToken returns null', async () => {
    mockGetToken.mockResolvedValueOnce(null);
    const user = userEvent.setup();

    render(<BillingPage />);
    await user.click(screen.getByRole('button', { name: /subscribe/i }));

    await waitFor(() => {
      expect(mockGetToken).toHaveBeenCalled();
    });
    expect(mockCreateCheckout).not.toHaveBeenCalled();
  });

  it('does not call openPortal if getToken returns null', async () => {
    mockGetToken.mockResolvedValueOnce(null);
    const user = userEvent.setup();

    render(<BillingPage />);
    await user.click(
      screen.getByRole('button', { name: /manage subscription/i })
    );

    await waitFor(() => {
      expect(mockGetToken).toHaveBeenCalled();
    });
    expect(mockOpenPortal).not.toHaveBeenCalled();
  });

  it('renders Free plan features', () => {
    render(<BillingPage />);
    expect(screen.getByText('1 project')).toBeInTheDocument();
    expect(screen.getByText('Basic support')).toBeInTheDocument();
    expect(screen.getByText('Community access')).toBeInTheDocument();
  });
});
