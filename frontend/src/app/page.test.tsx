/**
 * Tests for app/page.tsx — Landing page
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import Home from './page';


describe('Home (Landing Page)', () => {
  it('renders the main heading', () => {
    render(<Home />);
    expect(screen.getByText('DualStack')).toBeInTheDocument();
  });

  it('renders the subtitle', () => {
    render(<Home />);
    expect(screen.getByText('FastAPI + Next.js SaaS Starter Kit')).toBeInTheDocument();
  });

  it('renders the description text', () => {
    render(<Home />);
    expect(
      screen.getByText(/Production-ready full-stack template/)
    ).toBeInTheDocument();
  });

  it('renders Get Started link pointing to sign-up', () => {
    render(<Home />);
    const link = screen.getByRole('link', { name: /get started/i });
    expect(link).toHaveAttribute('href', '/sign-up');
  });

  it('renders Sign In link pointing to sign-in', () => {
    render(<Home />);
    const link = screen.getByRole('link', { name: /sign in/i });
    expect(link).toHaveAttribute('href', '/sign-in');
  });

  it('renders the features heading', () => {
    render(<Home />);
    expect(screen.getByText("What's Included")).toBeInTheDocument();
  });

  it('renders all feature cards', () => {
    render(<Home />);
    expect(screen.getByText('Authentication')).toBeInTheDocument();
    expect(screen.getByText('Database')).toBeInTheDocument();
    expect(screen.getByText('Billing')).toBeInTheDocument();
    expect(screen.getByText('FastAPI Backend')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('UI Components')).toBeInTheDocument();
  });
});
