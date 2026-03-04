import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ItemForm } from './item-form';

describe('ItemForm', () => {
  it('renders title, description, and status fields', () => {
    render(<ItemForm onSubmit={jest.fn()} />);

    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/status/i)).toBeInTheDocument();
  });

  it('renders submit button with "Create" text by default', () => {
    render(<ItemForm onSubmit={jest.fn()} />);
    expect(screen.getByRole('button', { name: /create/i })).toBeInTheDocument();
  });

  it('renders submit button with "Update" text when initialData is provided', () => {
    render(
      <ItemForm
        onSubmit={jest.fn()}
        initialData={{ title: 'Existing', description: 'Desc', status: 'active' }}
      />
    );
    expect(screen.getByRole('button', { name: /update/i })).toBeInTheDocument();
  });

  it('pre-fills fields with initialData', () => {
    render(
      <ItemForm
        onSubmit={jest.fn()}
        initialData={{ title: 'My Item', description: 'My desc', status: 'archived' }}
      />
    );

    expect(screen.getByLabelText(/title/i)).toHaveValue('My Item');
    expect(screen.getByLabelText(/description/i)).toHaveValue('My desc');
    expect(screen.getByLabelText(/status/i)).toHaveValue('archived');
  });

  it('calls onSubmit with form data when submitted', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn();
    render(<ItemForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/title/i), 'New Title');
    await user.type(screen.getByLabelText(/description/i), 'Some description');
    await user.click(screen.getByRole('button', { name: /create/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      title: 'New Title',
      description: 'Some description',
      status: 'draft',
    });
  });

  it('requires title field', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn();
    render(<ItemForm onSubmit={onSubmit} />);

    // Try to submit without title
    await user.click(screen.getByRole('button', { name: /create/i }));

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('submits with selected status', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn();
    render(<ItemForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/title/i), 'Test');
    await user.selectOptions(screen.getByLabelText(/status/i), 'active');
    await user.click(screen.getByRole('button', { name: /create/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      title: 'Test',
      description: '',
      status: 'active',
    });
  });

  it('disables submit button when isLoading is true', () => {
    render(<ItemForm onSubmit={jest.fn()} isLoading={true} />);
    expect(screen.getByRole('button', { name: /saving/i })).toBeDisabled();
  });

  it('does not submit when title is only whitespace', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn();
    render(<ItemForm onSubmit={onSubmit} />);

    // Type spaces into title (passes HTML required but fails trim check)
    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, '   ');
    await user.click(screen.getByRole('button', { name: /create/i }));

    expect(onSubmit).not.toHaveBeenCalled();
  });
});
