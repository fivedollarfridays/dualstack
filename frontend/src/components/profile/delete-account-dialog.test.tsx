/**
 * Tests for DeleteAccountDialog component.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DeleteAccountDialog } from './delete-account-dialog';

describe('DeleteAccountDialog', () => {
  it('shows initial delete button', () => {
    render(<DeleteAccountDialog onConfirm={jest.fn()} />);
    expect(screen.getByText('Delete Account')).toBeInTheDocument();
  });

  it('opens confirmation dialog on click', async () => {
    const user = userEvent.setup();
    render(<DeleteAccountDialog onConfirm={jest.fn()} />);

    await user.click(screen.getByText('Delete Account'));

    expect(screen.getByText('Delete Your Account')).toBeInTheDocument();
    expect(screen.getByText(/permanent and irreversible/)).toBeInTheDocument();
  });

  it('disables confirm button until phrase is typed', async () => {
    const user = userEvent.setup();
    render(<DeleteAccountDialog onConfirm={jest.fn()} />);

    await user.click(screen.getByText('Delete Account'));

    expect(screen.getByText('Permanently Delete')).toBeDisabled();
  });

  it('enables confirm button after typing the phrase', async () => {
    const user = userEvent.setup();
    render(<DeleteAccountDialog onConfirm={jest.fn()} />);

    await user.click(screen.getByText('Delete Account'));
    await user.type(screen.getByLabelText('Confirmation phrase'), 'DELETE MY ACCOUNT');

    expect(screen.getByText('Permanently Delete')).toBeEnabled();
  });

  it('calls onConfirm when confirmed', async () => {
    const user = userEvent.setup();
    const onConfirm = jest.fn();
    render(<DeleteAccountDialog onConfirm={onConfirm} />);

    await user.click(screen.getByText('Delete Account'));
    await user.type(screen.getByLabelText('Confirmation phrase'), 'DELETE MY ACCOUNT');
    await user.click(screen.getByText('Permanently Delete'));

    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('closes dialog on cancel', async () => {
    const user = userEvent.setup();
    render(<DeleteAccountDialog onConfirm={jest.fn()} />);

    await user.click(screen.getByText('Delete Account'));
    expect(screen.getByText('Delete Your Account')).toBeInTheDocument();

    await user.click(screen.getByText('Cancel'));
    expect(screen.queryByText('Delete Your Account')).not.toBeInTheDocument();
  });

  it('warns about data loss', async () => {
    const user = userEvent.setup();
    render(<DeleteAccountDialog onConfirm={jest.fn()} />);

    await user.click(screen.getByText('Delete Account'));

    expect(screen.getByText(/All your data, items, and subscription will be deleted/)).toBeInTheDocument();
  });

  it('shows deleting state when isDeleting is true', async () => {
    const user = userEvent.setup();
    render(<DeleteAccountDialog onConfirm={jest.fn()} isDeleting={true} />);

    await user.click(screen.getByText('Delete Account'));

    expect(screen.getByText('Deleting...')).toBeInTheDocument();
    expect(screen.getByText('Deleting...')).toBeDisabled();
  });
});
