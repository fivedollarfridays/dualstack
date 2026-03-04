/**
 * Tests for contexts/theme-context.tsx — ThemeProvider and useTheme hook
 */
import React from 'react';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, useTheme } from './theme-context';

// Helper component that exposes theme context values for testing
function ThemeConsumer() {
  const { theme, effectiveTheme, setTheme } = useTheme();
  return (
    <div>
      <span data-testid="theme">{theme}</span>
      <span data-testid="effective">{effectiveTheme}</span>
      <button onClick={() => setTheme('light')}>Set Light</button>
      <button onClick={() => setTheme('dark')}>Set Dark</button>
      <button onClick={() => setTheme('system')}>Set System</button>
    </div>
  );
}

// Track matchMedia listeners
let mediaChangeHandler: ((e: MediaQueryListEvent) => void) | null = null;

beforeEach(() => {
  localStorage.clear();
  document.documentElement.classList.remove('dark');
  mediaChangeHandler = null;

  // Mock matchMedia
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation((query: string) => ({
      matches: query === '(prefers-color-scheme: dark)',
      media: query,
      addEventListener: (_event: string, handler: (e: MediaQueryListEvent) => void) => {
        mediaChangeHandler = handler;
      },
      removeEventListener: jest.fn(),
    })),
  });
});

describe('ThemeProvider', () => {
  it('renders children', () => {
    render(
      <ThemeProvider>
        <span>child content</span>
      </ThemeProvider>
    );
    expect(screen.getByText('child content')).toBeInTheDocument();
  });

  it('provides default theme value of system', () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );
    expect(screen.getByTestId('theme')).toHaveTextContent('system');
  });

  it('resolves system theme to dark when prefers-color-scheme is dark', () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );
    // matchMedia returns matches:true for dark, so effective should be dark
    expect(screen.getByTestId('effective')).toHaveTextContent('dark');
  });

  it('adds dark class to documentElement when effective theme is dark', () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('removes dark class when effective theme is light', async () => {
    const user = userEvent.setup();
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );

    await user.click(screen.getByText('Set Light'));
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });
});

describe('useTheme', () => {
  it('throws when used outside ThemeProvider', () => {
    // Suppress console.error from React error boundary
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<ThemeConsumer />);
    }).toThrow('useTheme must be used within ThemeProvider');

    consoleSpy.mockRestore();
  });

  it('allows setting theme to light', async () => {
    const user = userEvent.setup();
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );

    await user.click(screen.getByText('Set Light'));
    expect(screen.getByTestId('theme')).toHaveTextContent('light');
    expect(screen.getByTestId('effective')).toHaveTextContent('light');
  });

  it('allows setting theme to dark', async () => {
    const user = userEvent.setup();
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );

    await user.click(screen.getByText('Set Dark'));
    expect(screen.getByTestId('theme')).toHaveTextContent('dark');
    expect(screen.getByTestId('effective')).toHaveTextContent('dark');
  });

  it('persists theme to localStorage', async () => {
    const user = userEvent.setup();
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );

    await user.click(screen.getByText('Set Dark'));
    expect(localStorage.getItem('dualstack-theme')).toBe('dark');
  });

  it('hydrates theme from localStorage on mount', () => {
    localStorage.setItem('dualstack-theme', 'light');

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme')).toHaveTextContent('light');
  });

  it('ignores invalid stored theme values', () => {
    localStorage.setItem('dualstack-theme', 'invalid-theme');

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );

    // Falls back to default 'system' when stored value is invalid
    expect(screen.getByTestId('theme')).toHaveTextContent('system');
  });

  it('responds to system theme changes to light via matchMedia listener', () => {
    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );

    // Simulate system theme changing to light
    expect(mediaChangeHandler).not.toBeNull();
    act(() => {
      mediaChangeHandler!({ matches: false } as MediaQueryListEvent);
    });

    expect(screen.getByTestId('effective')).toHaveTextContent('light');
  });

  it('responds to system theme changes to dark via matchMedia listener', () => {
    // Start with light system preference so we can test changing to dark
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation((query: string) => ({
        matches: false, // start light
        media: query,
        addEventListener: (_event: string, handler: (e: MediaQueryListEvent) => void) => {
          mediaChangeHandler = handler;
        },
        removeEventListener: jest.fn(),
      })),
    });

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );

    // Simulate system theme changing to dark
    expect(mediaChangeHandler).not.toBeNull();
    act(() => {
      mediaChangeHandler!({ matches: true } as MediaQueryListEvent);
    });

    expect(screen.getByTestId('effective')).toHaveTextContent('dark');
  });

  it('resolves system theme to light when system preference is light', () => {
    // Override matchMedia to return light preference
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation((query: string) => ({
        matches: false, // not dark
        media: query,
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
      })),
    });

    render(
      <ThemeProvider>
        <ThemeConsumer />
      </ThemeProvider>
    );

    expect(screen.getByTestId('effective')).toHaveTextContent('light');
  });
});
