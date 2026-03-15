/**
 * Tests for FileUpload component.
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { FileUpload } from './file-upload';

describe('FileUpload', () => {
  it('renders drop zone with instructions', () => {
    render(<FileUpload onUpload={jest.fn()} />);
    expect(screen.getByText(/drag and drop/i)).toBeInTheDocument();
  });

  it('calls onUpload when a file is selected via input', () => {
    const onUpload = jest.fn();
    render(<FileUpload onUpload={onUpload} />);

    const input = screen.getByTestId('file-input');
    const file = new File(['data'], 'photo.png', { type: 'image/png' });
    fireEvent.change(input, { target: { files: [file] } });

    expect(onUpload).toHaveBeenCalledWith(file);
  });

  it('shows error for oversized files', () => {
    const onUpload = jest.fn();
    render(<FileUpload onUpload={onUpload} maxSizeMB={1} />);

    const input = screen.getByTestId('file-input');
    // Create a file mock that's > 1MB
    const bigFile = new File(['x'.repeat(2 * 1024 * 1024)], 'big.bin', { type: 'application/octet-stream' });
    fireEvent.change(input, { target: { files: [bigFile] } });

    expect(screen.getByText(/exceeds 1MB/i)).toBeInTheDocument();
    expect(onUpload).not.toHaveBeenCalled();
  });

  it('does not trigger upload when disabled', () => {
    const onUpload = jest.fn();
    render(<FileUpload onUpload={onUpload} disabled />);

    const dropZone = screen.getByRole('button');
    expect(dropZone).toHaveClass('opacity-50');
  });

  it('shows drop text on drag over', () => {
    render(<FileUpload onUpload={jest.fn()} />);
    const dropZone = screen.getByRole('button');

    fireEvent.dragOver(dropZone, { preventDefault: jest.fn() });
    expect(screen.getByText('Drop file here')).toBeInTheDocument();
  });
});
