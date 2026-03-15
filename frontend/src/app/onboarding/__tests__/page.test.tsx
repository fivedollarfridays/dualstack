/**
 * Tests for onboarding page.
 */
import { render, screen, fireEvent } from '@testing-library/react';

const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
  redirect: jest.fn(),
}));

import OnboardingPage from '../page';

beforeEach(() => {
  localStorage.clear();
  mockPush.mockReset();
});

describe('OnboardingPage', () => {
  it('renders the wizard starting at Welcome step', () => {
    render(<OnboardingPage />);

    expect(screen.getByRole('heading', { name: /welcome/i })).toBeInTheDocument();
    expect(screen.getByText('Step 1 of 4')).toBeInTheDocument();
  });

  it('navigates through all 4 steps', () => {
    render(<OnboardingPage />);

    // Step 1: Welcome
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    // Step 2: Preferences
    expect(screen.getByText('Step 2 of 4')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /preferences/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    // Step 3: First Item
    expect(screen.getByText('Step 3 of 4')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /first item/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    // Step 4: Completion
    expect(screen.getByText('Step 4 of 4')).toBeInTheDocument();
    expect(screen.getByText(/all set/i)).toBeInTheDocument();
  });

  it('redirects to dashboard when already completed', () => {
    localStorage.setItem('dualstack-onboarding-complete', 'true');

    render(<OnboardingPage />);

    expect(mockPush).toHaveBeenCalledWith('/dashboard');
  });
});
