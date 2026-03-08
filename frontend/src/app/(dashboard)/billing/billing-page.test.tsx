/**
 * Tests for app/(dashboard)/billing/page.tsx -- Billing page
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BillingPage from './page';

// Mock the billing API
const mockCreateCheckout = jest.fn();
jest.mock('@/lib/api/billing', () => ({
  createCheckout: (...args: unknown[]) => mockCreateCheckout(...args),
}));

const mockGetToken = jest.fn();
jest.mock('@/contexts/auth-context', () => ({
  useAppAuth: () => ({
    userId: 'test-user-123',
    isLoaded: true,
    isSignedIn: true,
    getToken: mockGetToken,
  }),
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

  it('calls createCheckout with token and price on Subscribe click', async () => {
    const user = userEvent.setup();
    mockCreateCheckout.mockResolvedValueOnce('https://checkout.stripe.com/session123');

    render(<BillingPage />);
    await user.click(screen.getByRole('button', { name: /subscribe/i }));

    await waitFor(() => {
      expect(mockCreateCheckout).toHaveBeenCalledWith(
        'mock-token',
        'price_pro_monthly',
        'http://localhost/billing?success=true',
        'http://localhost/billing'
      );
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

  it('renders Free plan features', () => {
    render(<BillingPage />);
    expect(screen.getByText('1 project')).toBeInTheDocument();
    expect(screen.getByText('Basic support')).toBeInTheDocument();
    expect(screen.getByText('Community access')).toBeInTheDocument();
  });

  it('displays error when createCheckout fails', async () => {
    const user = userEvent.setup();
    mockCreateCheckout.mockRejectedValueOnce(new Error('Checkout failed'));

    render(<BillingPage />);
    await user.click(screen.getByRole('button', { name: /subscribe/i }));

    await waitFor(() => {
      expect(
        screen.getByText('Failed to start checkout. Please try again.')
      ).toBeInTheDocument();
    });
  });

  it('shows error when checkout returns invalid redirect URL', async () => {
    const user = userEvent.setup();
    mockCreateCheckout.mockResolvedValueOnce('https://evil.com/steal-data');

    render(<BillingPage />);
    await user.click(screen.getByRole('button', { name: /subscribe/i }));

    await waitFor(() => {
      expect(
        screen.getByText('Invalid checkout URL received. Please try again.')
      ).toBeInTheDocument();
    });
  });

  it('clears previous error on new subscribe attempt', async () => {
    const user = userEvent.setup();
    mockCreateCheckout.mockRejectedValueOnce(new Error('Checkout failed'));

    render(<BillingPage />);
    await user.click(screen.getByRole('button', { name: /subscribe/i }));

    await waitFor(() => {
      expect(
        screen.getByText('Failed to start checkout. Please try again.')
      ).toBeInTheDocument();
    });

    // Second attempt succeeds: error should be cleared
    mockCreateCheckout.mockResolvedValueOnce('https://checkout.stripe.com/ok');
    await user.click(screen.getByRole('button', { name: /subscribe/i }));

    await waitFor(() => {
      expect(
        screen.queryByText('Failed to start checkout. Please try again.')
      ).not.toBeInTheDocument();
    });
  });
});
