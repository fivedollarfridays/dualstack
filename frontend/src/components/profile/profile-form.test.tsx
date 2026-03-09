/**
 * Tests for ProfileForm component.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ProfileForm } from './profile-form';

describe('ProfileForm', () => {
  it('renders with current display name', () => {
    render(<ProfileForm displayName="Alice" onSave={jest.fn()} />);
    expect(screen.getByDisplayValue('Alice')).toBeInTheDocument();
  });

  it('calls onSave with updated name on submit', async () => {
    const user = userEvent.setup();
    const onSave = jest.fn();
    render(<ProfileForm displayName="Alice" onSave={onSave} />);

    const input = screen.getByDisplayValue('Alice');
    await user.clear(input);
    await user.type(input, 'Bob');
    await user.click(screen.getByText('Save'));

    expect(onSave).toHaveBeenCalledWith('Bob');
  });

  it('shows saving state', () => {
    render(<ProfileForm displayName="Alice" onSave={jest.fn()} isSaving />);
    expect(screen.getByText('Saving...')).toBeInTheDocument();
  });

  it('disables button while saving', () => {
    render(<ProfileForm displayName="Alice" onSave={jest.fn()} isSaving />);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
