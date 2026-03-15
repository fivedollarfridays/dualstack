/**
 * Tests for WelcomeStep component.
 */
import { render, screen } from '@testing-library/react';
import { WelcomeStep } from '../welcome-step';

describe('WelcomeStep', () => {
  it('renders welcome heading', () => {
    render(<WelcomeStep />);
    expect(screen.getByRole('heading', { name: /welcome/i })).toBeInTheDocument();
  });

  it('renders app description text', () => {
    render(<WelcomeStep />);
    expect(screen.getByText(/get started/i)).toBeInTheDocument();
  });
});
