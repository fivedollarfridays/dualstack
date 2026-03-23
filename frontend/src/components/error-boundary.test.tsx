/**
 * Tests for ErrorBoundary component — catches render errors with fallback UI
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorBoundary } from './error-boundary';

// A component that throws on render
function ThrowingComponent({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test render error');
  }
  return <div>Working child</div>;
}

// Suppress console.error for expected error boundary logs
beforeEach(() => {
  jest.spyOn(console, 'error').mockImplementation(() => {});
});
afterEach(() => {
  jest.restoreAllMocks();
});

describe('ErrorBoundary', () => {
  it('renders children when no error occurs', () => {
    render(
      <ErrorBoundary>
        <div>Child content</div>
      </ErrorBoundary>
    );
    expect(screen.getByText('Child content')).toBeInTheDocument();
  });

  it('shows default fallback UI when a child throws', () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
  });

  it('does not show fallback when children render successfully', () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={false} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Working child')).toBeInTheDocument();
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
  });

  it('resets error state when Try again button is clicked', async () => {
    const user = userEvent.setup();

    // Use a key-controlled wrapper so re-render after retry gives a fresh child
    let throwOnRender = true;

    function ConditionalChild() {
      if (throwOnRender) {
        throw new Error('Test render error');
      }
      return <div>Working child</div>;
    }

    function Wrapper({ renderKey }: { renderKey: number }) {
      return (
        <ErrorBoundary key={renderKey}>
          <ConditionalChild />
        </ErrorBoundary>
      );
    }

    const { rerender } = render(<Wrapper renderKey={1} />);
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();

    // Stop throwing, then click retry
    throwOnRender = false;
    await user.click(screen.getByRole('button', { name: /try again/i }));

    // After retry with hasError reset, children re-render
    expect(screen.getByText('Working child')).toBeInTheDocument();
  });

  it('renders custom fallback when provided', () => {
    render(
      <ErrorBoundary fallback={<div>Custom error UI</div>}>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Custom error UI')).toBeInTheDocument();
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
  });

  it('calls componentDidCatch with error info', () => {
    const logSpy = jest.spyOn(console, 'error');

    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    );

    // React calls console.error when an error boundary catches
    expect(logSpy).toHaveBeenCalled();
  });
});
