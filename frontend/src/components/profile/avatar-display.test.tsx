/**
 * Tests for AvatarDisplay component.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { AvatarDisplay } from './avatar-display';

describe('AvatarDisplay', () => {
  it('renders image when avatarUrl is provided', () => {
    render(<AvatarDisplay avatarUrl="https://img.example.com/a.png" displayName="Alice" />);
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', 'https://img.example.com/a.png');
    expect(img).toHaveAttribute('alt', 'Alice');
  });

  it('renders initials fallback when no avatarUrl', () => {
    render(<AvatarDisplay avatarUrl={null} displayName="Bob Smith" />);
    expect(screen.getByText('BS')).toBeInTheDocument();
  });

  it('renders ? when no name and no avatar', () => {
    render(<AvatarDisplay avatarUrl={null} displayName={null} />);
    expect(screen.getByText('?')).toBeInTheDocument();
  });

  it('handles single-word name', () => {
    render(<AvatarDisplay avatarUrl={null} displayName="Alice" />);
    expect(screen.getByText('A')).toBeInTheDocument();
  });

  it('uses fallback alt text when avatarUrl is set but displayName is null', () => {
    render(<AvatarDisplay avatarUrl="https://img.example.com/a.png" displayName={null} />);
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('alt', 'User avatar');
  });
});
