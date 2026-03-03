import '@testing-library/jest-dom';
import React from 'react';

// Mock scrollIntoView since JSDOM doesn't support it
window.HTMLElement.prototype.scrollIntoView = jest.fn();

// Mock next/image to render a standard img element for testing
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: React.ImgHTMLAttributes<HTMLImageElement> & { priority?: boolean; unoptimized?: boolean }) => {
    const { priority, unoptimized, ...imgProps } = props;
    return React.createElement('img', imgProps);
  },
}));

// Mock @clerk/nextjs to avoid ESM issues in Jest
jest.mock('@clerk/nextjs', () => ({
  useUser: () => ({ user: { id: 'test-user-123' }, isLoaded: true, isSignedIn: true }),
  useAuth: () => ({ userId: 'test-user-123', isLoaded: true, isSignedIn: true }),
  useClerk: () => ({ signOut: jest.fn() }),
  ClerkProvider: ({ children }: { children: React.ReactNode }) => children,
  SignedIn: ({ children }: { children: React.ReactNode }) => children,
  SignedOut: ({ children }: { children: React.ReactNode }) => null,
  UserButton: () => null,
}));
