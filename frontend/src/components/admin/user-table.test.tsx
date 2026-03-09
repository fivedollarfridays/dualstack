/**
 * Tests for admin UserTable component.
 */
import React from 'react';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserTable } from './user-table';
import type { AdminUser } from '@/lib/api/admin';

const mockUsers: AdminUser[] = [
  {
    id: 'id-1',
    clerk_user_id: 'clerk-user-1',
    role: 'member',
    subscription_plan: 'free',
    subscription_status: 'none',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 'id-2',
    clerk_user_id: 'clerk-admin-1',
    role: 'admin',
    subscription_plan: 'pro',
    subscription_status: 'active',
    created_at: '2026-02-01T00:00:00Z',
    updated_at: '2026-02-01T00:00:00Z',
  },
];

describe('UserTable', () => {
  it('renders user rows', () => {
    render(<UserTable users={mockUsers} onRoleChange={jest.fn()} />);
    expect(screen.getByText('clerk-user-1')).toBeInTheDocument();
    expect(screen.getByText('clerk-admin-1')).toBeInTheDocument();
  });

  it('shows empty message when no users', () => {
    render(<UserTable users={[]} onRoleChange={jest.fn()} />);
    expect(screen.getByText('No users found.')).toBeInTheDocument();
  });

  it('displays role badges', () => {
    render(<UserTable users={mockUsers} onRoleChange={jest.fn()} />);
    // Role text appears in both badges and select options
    const memberElements = screen.getAllByText('member');
    expect(memberElements.length).toBeGreaterThanOrEqual(1);
    const adminElements = screen.getAllByText('admin');
    expect(adminElements.length).toBeGreaterThanOrEqual(1);
  });

  it('calls onRoleChange when role select changes', async () => {
    const user = userEvent.setup();
    const onRoleChange = jest.fn();
    render(<UserTable users={mockUsers} onRoleChange={onRoleChange} />);

    const selects = screen.getAllByRole('combobox');
    await user.selectOptions(selects[0], 'admin');

    expect(onRoleChange).toHaveBeenCalledWith('id-1', 'admin');
  });

  it('renders table headers', () => {
    render(<UserTable users={mockUsers} onRoleChange={jest.fn()} />);
    expect(screen.getByText('User ID')).toBeInTheDocument();
    expect(screen.getByText('Role')).toBeInTheDocument();
    expect(screen.getByText('Plan')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
  });

  it('shows free when subscription_plan is null', () => {
    const userWithNullPlan: AdminUser[] = [{
      id: 'id-3',
      clerk_user_id: 'clerk-user-3',
      role: 'member',
      subscription_plan: null,
      subscription_status: null,
      created_at: '2026-03-01T00:00:00Z',
      updated_at: '2026-03-01T00:00:00Z',
    }];
    render(<UserTable users={userWithNullPlan} onRoleChange={jest.fn()} />);
    // The cell should display 'free' as fallback
    const row = screen.getByText('clerk-user-3').closest('tr')!;
    expect(within(row).getByText('free')).toBeInTheDocument();
  });
});
