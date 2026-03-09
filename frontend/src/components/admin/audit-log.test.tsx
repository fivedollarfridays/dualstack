/**
 * Tests for admin AuditLog component.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuditLog } from './audit-log';
import type { AuditEntry } from '@/lib/api/admin';

const mockEntries: AuditEntry[] = [
  {
    id: 'log-1',
    user_id: 'user-1',
    action: 'create',
    resource_type: 'item',
    resource_id: 'item-1',
    outcome: 'success',
    detail: '',
    created_at: '2026-01-01T12:00:00Z',
  },
  {
    id: 'log-2',
    user_id: 'user-2',
    action: 'auth.failed',
    resource_type: 'token',
    resource_id: 'unknown',
    outcome: 'failure',
    detail: 'bad token',
    created_at: '2026-01-01T13:00:00Z',
  },
];

describe('AuditLog', () => {
  it('renders entries', () => {
    render(<AuditLog entries={mockEntries} total={2} page={1} onPageChange={jest.fn()} />);
    expect(screen.getByText('create')).toBeInTheDocument();
    expect(screen.getByText('auth.failed')).toBeInTheDocument();
  });

  it('shows empty message when no entries', () => {
    render(<AuditLog entries={[]} total={0} page={1} onPageChange={jest.fn()} />);
    expect(screen.getByText('No audit log entries.')).toBeInTheDocument();
  });

  it('shows outcome badges', () => {
    render(<AuditLog entries={mockEntries} total={2} page={1} onPageChange={jest.fn()} />);
    expect(screen.getByText('success')).toBeInTheDocument();
    expect(screen.getByText('failure')).toBeInTheDocument();
  });

  it('shows pagination when total exceeds limit', async () => {
    const user = userEvent.setup();
    const onPageChange = jest.fn();
    render(
      <AuditLog entries={mockEntries} total={100} page={1} limit={50} onPageChange={onPageChange} />
    );
    expect(screen.getByText('Page 1 of 2')).toBeInTheDocument();
    await user.click(screen.getByText('Next'));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it('navigates to previous page', async () => {
    const user = userEvent.setup();
    const onPageChange = jest.fn();
    render(
      <AuditLog entries={mockEntries} total={100} page={2} limit={50} onPageChange={onPageChange} />
    );
    await user.click(screen.getByText('Previous'));
    expect(onPageChange).toHaveBeenCalledWith(1);
  });

  it('disables Previous on first page', () => {
    render(
      <AuditLog entries={mockEntries} total={100} page={1} limit={50} onPageChange={jest.fn()} />
    );
    expect(screen.getByText('Previous')).toBeDisabled();
  });

  it('disables Next on last page', () => {
    render(
      <AuditLog entries={mockEntries} total={100} page={2} limit={50} onPageChange={jest.fn()} />
    );
    expect(screen.getByText('Next')).toBeDisabled();
  });

  it('does not show pagination when total is within limit', () => {
    render(<AuditLog entries={mockEntries} total={2} page={1} onPageChange={jest.fn()} />);
    expect(screen.queryByText('Previous')).not.toBeInTheDocument();
    expect(screen.queryByText('Next')).not.toBeInTheDocument();
  });
});
