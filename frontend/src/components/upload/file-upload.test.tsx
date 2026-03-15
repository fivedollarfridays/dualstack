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

  it('calls onUpload when a file is dropped', () => {
    const onUpload = jest.fn();
    render(<FileUpload onUpload={onUpload} />);
    const dropZone = screen.getByRole('button');

    const file = new File(['hello'], 'doc.txt', { type: 'text/plain' });
    fireEvent.drop(dropZone, { dataTransfer: { files: [file] } });

    expect(onUpload).toHaveBeenCalledWith(file);
  });

  it('does not call onUpload on drop when disabled', () => {
    const onUpload = jest.fn();
    render(<FileUpload onUpload={onUpload} disabled />);
    const dropZone = screen.getByRole('button');

    const file = new File(['hello'], 'doc.txt', { type: 'text/plain' });
    fireEvent.drop(dropZone, { dataTransfer: { files: [file] } });

    expect(onUpload).not.toHaveBeenCalled();
  });

  it('removes drag highlight on drag leave', () => {
    render(<FileUpload onUpload={jest.fn()} />);
    const dropZone = screen.getByRole('button');

    fireEvent.dragOver(dropZone, { preventDefault: jest.fn() });
    expect(screen.getByText('Drop file here')).toBeInTheDocument();

    fireEvent.dragLeave(dropZone);
    expect(screen.getByText(/drag and drop/i)).toBeInTheDocument();
  });

  it('opens file picker on click when not disabled', () => {
    const onUpload = jest.fn();
    render(<FileUpload onUpload={onUpload} />);
    const dropZone = screen.getByRole('button');
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    const clickSpy = jest.spyOn(input, 'click');
    fireEvent.click(dropZone);

    expect(clickSpy).toHaveBeenCalled();
    clickSpy.mockRestore();
  });

  it('does not open file picker on click when disabled', () => {
    render(<FileUpload onUpload={jest.fn()} disabled />);
    const dropZone = screen.getByRole('button');
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    const clickSpy = jest.spyOn(input, 'click');
    fireEvent.click(dropZone);

    expect(clickSpy).not.toHaveBeenCalled();
    clickSpy.mockRestore();
  });

  it('handles drop with empty files list', () => {
    const onUpload = jest.fn();
    render(<FileUpload onUpload={onUpload} />);
    const dropZone = screen.getByRole('button');

    fireEvent.drop(dropZone, { dataTransfer: { files: [] } });
    expect(onUpload).not.toHaveBeenCalled();
  });

  it('handles file input change with no file selected', () => {
    const onUpload = jest.fn();
    render(<FileUpload onUpload={onUpload} />);
    const input = screen.getByTestId('file-input');

    fireEvent.change(input, { target: { files: [] } });
    expect(onUpload).not.toHaveBeenCalled();
  });

  it('handles file input change with null files', () => {
    const onUpload = jest.fn();
    render(<FileUpload onUpload={onUpload} />);
    const input = screen.getByTestId('file-input');

    fireEvent.change(input, { target: { files: null } });
    expect(onUpload).not.toHaveBeenCalled();
  });

  it('opens file picker on Enter/Space keydown', () => {
    render(<FileUpload onUpload={jest.fn()} />);
    const dropZone = screen.getByRole('button');
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    const clickSpy = jest.spyOn(input, 'click');
    fireEvent.keyDown(dropZone, { key: 'Enter' });
    // Enter triggers both the keydown handler and the default button click in jsdom
    expect(clickSpy.mock.calls.length).toBeGreaterThanOrEqual(1);

    clickSpy.mockClear();
    fireEvent.keyDown(dropZone, { key: ' ' });
    expect(clickSpy).toHaveBeenCalled();
    clickSpy.mockRestore();
  });

  it('does not open file picker on unrelated key press', () => {
    render(<FileUpload onUpload={jest.fn()} />);
    const dropZone = screen.getByRole('button');
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    const clickSpy = jest.spyOn(input, 'click');
    fireEvent.keyDown(dropZone, { key: 'Tab' });
    expect(clickSpy).not.toHaveBeenCalled();
    clickSpy.mockRestore();
  });
});
