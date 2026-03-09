/**
 * Tests for admin HealthOverview component.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { HealthOverview } from './health-overview';

describe('HealthOverview', () => {
  it('renders healthy status in green', () => {
    render(
      <HealthOverview health={{ status: 'healthy', database: 'connected', user_count: 10 }} />
    );
    expect(screen.getByText('healthy')).toBeInTheDocument();
    expect(screen.getByText('connected')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  it('renders unhealthy status in red', () => {
    render(
      <HealthOverview
        health={{ status: 'unhealthy', database: 'error', user_count: 0 }}
      />
    );
    expect(screen.getByText('unhealthy')).toBeInTheDocument();
    expect(screen.getByText('error')).toBeInTheDocument();
  });

  it('shows user count', () => {
    render(
      <HealthOverview health={{ status: 'healthy', database: 'connected', user_count: 42 }} />
    );
    expect(screen.getByText('42')).toBeInTheDocument();
  });
});
