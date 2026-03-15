/**
 * Tests for UploadProgress component.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { UploadProgress } from './upload-progress';

describe('UploadProgress', () => {
  it('renders filename and percentage', () => {
    render(<UploadProgress filename="photo.png" percent={45} />);
    expect(screen.getByText('photo.png')).toBeInTheDocument();
    expect(screen.getByText('45%')).toBeInTheDocument();
  });

  it('renders a progressbar with correct aria value', () => {
    render(<UploadProgress filename="doc.pdf" percent={75} />);
    const bar = screen.getByRole('progressbar');
    expect(bar).toHaveAttribute('aria-valuenow', '75');
  });

  it('renders 0% at start', () => {
    render(<UploadProgress filename="file.txt" percent={0} />);
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('renders 100% when complete', () => {
    render(<UploadProgress filename="file.txt" percent={100} />);
    expect(screen.getByText('100%')).toBeInTheDocument();
  });
});
