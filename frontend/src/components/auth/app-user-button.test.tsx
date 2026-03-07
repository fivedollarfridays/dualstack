/**
 * Tests for components/auth/app-user-button.tsx
 */
import React from 'react';
import { render, screen } from '@testing-library/react';

// Mock auth-config to control isClerkEnabled
const mockIsClerkEnabled = jest.fn();
jest.mock('@/lib/auth-config', () => ({
  isClerkEnabled: () => mockIsClerkEnabled(),
}));

import { AppUserButton } from './app-user-button';

describe('AppUserButton', () => {
  it('renders DevUserButton when Clerk is disabled', () => {
    mockIsClerkEnabled.mockReturnValue(false);
    render(<AppUserButton />);
    expect(screen.getByText('D')).toBeInTheDocument();
  });

  it('renders Clerk UserButton when Clerk is enabled', () => {
    mockIsClerkEnabled.mockReturnValue(true);
    render(<AppUserButton />);
    // The UserButton mock from jest.setup.ts returns null,
    // so DevUserButton 'D' should NOT be present
    expect(screen.queryByText('D')).not.toBeInTheDocument();
  });
});
