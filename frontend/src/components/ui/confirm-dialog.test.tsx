import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ConfirmDialog } from './confirm-dialog';

describe('ConfirmDialog', () => {
  it('renders nothing when not open', () => {
    render(
      <ConfirmDialog
        open={false}
        title="Delete?"
        message="Are you sure?"
        onConfirm={jest.fn()}
        onCancel={jest.fn()}
      />
    );
    expect(screen.queryByText('Delete?')).not.toBeInTheDocument();
  });

  it('renders title and message when open', () => {
    render(
      <ConfirmDialog
        open={true}
        title="Delete Item"
        message="This action cannot be undone."
        onConfirm={jest.fn()}
        onCancel={jest.fn()}
      />
    );
    expect(screen.getByText('Delete Item')).toBeInTheDocument();
    expect(screen.getByText('This action cannot be undone.')).toBeInTheDocument();
  });

  it('calls onConfirm when confirm button is clicked', async () => {
    const user = userEvent.setup();
    const onConfirm = jest.fn();
    render(
      <ConfirmDialog
        open={true}
        title="Delete?"
        message="Are you sure?"
        onConfirm={onConfirm}
        onCancel={jest.fn()}
      />
    );
    await user.click(screen.getByRole('button', { name: /confirm/i }));
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onCancel when cancel button is clicked', async () => {
    const user = userEvent.setup();
    const onCancel = jest.fn();
    render(
      <ConfirmDialog
        open={true}
        title="Delete?"
        message="Are you sure?"
        onConfirm={jest.fn()}
        onCancel={onCancel}
      />
    );
    await user.click(screen.getByRole('button', { name: /cancel/i }));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('renders with custom confirm label', () => {
    render(
      <ConfirmDialog
        open={true}
        title="Delete?"
        message="Are you sure?"
        confirmLabel="Yes, delete"
        onConfirm={jest.fn()}
        onCancel={jest.fn()}
      />
    );
    expect(screen.getByRole('button', { name: /yes, delete/i })).toBeInTheDocument();
  });

  it('has role="dialog" and aria-modal when open', () => {
    render(
      <ConfirmDialog
        open={true}
        title="Delete?"
        message="Are you sure?"
        onConfirm={jest.fn()}
        onCancel={jest.fn()}
      />
    );
    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby', 'confirm-dialog-title');
  });

  it('calls onCancel when Escape key is pressed', async () => {
    const user = userEvent.setup();
    const onCancel = jest.fn();
    render(
      <ConfirmDialog
        open={true}
        title="Delete?"
        message="Are you sure?"
        onConfirm={jest.fn()}
        onCancel={onCancel}
      />
    );
    await user.keyboard('{Escape}');
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('does not call onCancel for non-Escape keys', async () => {
    const user = userEvent.setup();
    const onCancel = jest.fn();
    render(
      <ConfirmDialog
        open={true}
        title="Delete?"
        message="Are you sure?"
        onConfirm={jest.fn()}
        onCancel={onCancel}
      />
    );
    await user.keyboard('a');
    expect(onCancel).not.toHaveBeenCalled();
  });

  it('traps focus forward with Tab within the dialog', async () => {
    const user = userEvent.setup();
    render(
      <ConfirmDialog
        open={true}
        title="Delete?"
        message="Are you sure?"
        confirmLabel="Delete"
        onConfirm={jest.fn()}
        onCancel={jest.fn()}
      />
    );
    const cancelBtn = screen.getByRole('button', { name: /cancel/i });
    const confirmBtn = screen.getByRole('button', { name: /delete/i });

    // Cancel button should be focused initially
    expect(cancelBtn).toHaveFocus();

    // Tab to confirm button
    await user.tab();
    expect(confirmBtn).toHaveFocus();

    // Tab should wrap back to cancel button (focus trap)
    await user.tab();
    expect(cancelBtn).toHaveFocus();
  });

  it('traps focus backward with Shift+Tab within the dialog', async () => {
    const user = userEvent.setup();
    render(
      <ConfirmDialog
        open={true}
        title="Delete?"
        message="Are you sure?"
        confirmLabel="Delete"
        onConfirm={jest.fn()}
        onCancel={jest.fn()}
      />
    );
    const cancelBtn = screen.getByRole('button', { name: /cancel/i });
    const confirmBtn = screen.getByRole('button', { name: /delete/i });

    // Cancel button should be focused initially
    expect(cancelBtn).toHaveFocus();

    // Shift+Tab should wrap to last focusable element (confirm button)
    await user.keyboard('{Shift>}{Tab}{/Shift}');
    expect(confirmBtn).toHaveFocus();
  });
});
