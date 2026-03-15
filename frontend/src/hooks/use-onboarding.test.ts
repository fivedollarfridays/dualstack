/**
 * Tests for useOnboarding hook.
 */
import { renderHook, act } from '@testing-library/react';

// Mock next/navigation
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}));

import { useOnboarding, ONBOARDING_STORAGE_KEY } from './use-onboarding';

beforeEach(() => {
  localStorage.clear();
  mockPush.mockReset();
});

describe('useOnboarding', () => {
  it('starts at step 0', () => {
    const { result } = renderHook(() => useOnboarding());

    expect(result.current.currentStep).toBe(0);
    expect(result.current.isComplete).toBe(false);
  });

  it('advances and goes back between steps', () => {
    const { result } = renderHook(() => useOnboarding());

    act(() => result.current.nextStep());
    expect(result.current.currentStep).toBe(1);

    act(() => result.current.nextStep());
    expect(result.current.currentStep).toBe(2);

    act(() => result.current.prevStep());
    expect(result.current.currentStep).toBe(1);
  });

  it('does not go below step 0', () => {
    const { result } = renderHook(() => useOnboarding());

    act(() => result.current.prevStep());
    expect(result.current.currentStep).toBe(0);
  });

  it('skip marks onboarding complete and redirects to dashboard', () => {
    const { result } = renderHook(() => useOnboarding());

    act(() => result.current.skip());

    expect(result.current.isComplete).toBe(true);
    expect(localStorage.getItem(ONBOARDING_STORAGE_KEY)).toBe('true');
    expect(mockPush).toHaveBeenCalledWith('/dashboard');
  });

  it('complete marks onboarding complete and redirects to dashboard', () => {
    const { result } = renderHook(() => useOnboarding());

    act(() => result.current.complete());

    expect(result.current.isComplete).toBe(true);
    expect(localStorage.getItem(ONBOARDING_STORAGE_KEY)).toBe('true');
    expect(mockPush).toHaveBeenCalledWith('/dashboard');
  });

  it('reads isComplete from localStorage on mount', () => {
    localStorage.setItem(ONBOARDING_STORAGE_KEY, 'true');

    const { result } = renderHook(() => useOnboarding());

    expect(result.current.isComplete).toBe(true);
  });

  it('does not exceed last step', () => {
    const { result } = renderHook(() => useOnboarding());

    // Advance to step 3 (last valid step, 0-indexed with 4 total)
    act(() => result.current.nextStep());
    act(() => result.current.nextStep());
    act(() => result.current.nextStep());
    expect(result.current.currentStep).toBe(3);

    // Should stay at step 3
    act(() => result.current.nextStep());
    expect(result.current.currentStep).toBe(3);
  });

  it('defaults isComplete to false when window is undefined', () => {
    const origWindow = globalThis.window;
    // @ts-expect-error -- simulate SSR by removing window
    delete (globalThis as Record<string, unknown>).window;

    const { result } = renderHook(() => useOnboarding());

    expect(result.current.isComplete).toBe(false);

    globalThis.window = origWindow;
  });
});
