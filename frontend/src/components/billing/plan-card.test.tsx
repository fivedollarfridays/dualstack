import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PlanCard } from './plan-card';

describe('PlanCard', () => {
  const defaultProps = {
    name: 'Pro',
    price: '$10/mo',
    features: ['Unlimited projects', 'Priority support', 'API access'],
    isCurrent: false,
    onSubscribe: jest.fn(),
  };

  beforeEach(() => {
    defaultProps.onSubscribe.mockReset();
  });

  it('renders plan name and price', () => {
    render(<PlanCard {...defaultProps} />);

    expect(screen.getByText('Pro')).toBeInTheDocument();
    expect(screen.getByText('$10/mo')).toBeInTheDocument();
  });

  it('renders all features', () => {
    render(<PlanCard {...defaultProps} />);

    expect(screen.getByText('Unlimited projects')).toBeInTheDocument();
    expect(screen.getByText('Priority support')).toBeInTheDocument();
    expect(screen.getByText('API access')).toBeInTheDocument();
  });

  it('shows Subscribe button when not current plan', () => {
    render(<PlanCard {...defaultProps} />);

    const button = screen.getByRole('button', { name: /subscribe/i });
    expect(button).toBeInTheDocument();
    expect(button).toBeEnabled();
  });

  it('shows Current Plan button when is current plan', () => {
    render(<PlanCard {...defaultProps} isCurrent={true} />);

    const button = screen.getByRole('button', { name: /current plan/i });
    expect(button).toBeInTheDocument();
    expect(button).toBeDisabled();
  });

  it('calls onSubscribe when Subscribe button is clicked', async () => {
    const user = userEvent.setup();
    render(<PlanCard {...defaultProps} />);

    await user.click(screen.getByRole('button', { name: /subscribe/i }));

    expect(defaultProps.onSubscribe).toHaveBeenCalledTimes(1);
  });

  it('does not call onSubscribe when current plan button is clicked', async () => {
    const user = userEvent.setup();
    render(<PlanCard {...defaultProps} isCurrent={true} />);

    const button = screen.getByRole('button', { name: /current plan/i });
    await user.click(button);

    expect(defaultProps.onSubscribe).not.toHaveBeenCalled();
  });
});
