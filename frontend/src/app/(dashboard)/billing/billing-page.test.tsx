import React from 'react';
import { render, screen } from '@testing-library/react';
import BillingPage from './page';

// Mock the billing API
jest.mock('@/lib/api/billing', () => ({
  createCheckout: jest.fn(),
  openPortal: jest.fn(),
}));

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
});
