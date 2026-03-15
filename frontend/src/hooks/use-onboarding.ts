import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export const ONBOARDING_STORAGE_KEY = 'dualstack-onboarding-complete';
export const TOTAL_STEPS = 4;

export function useOnboarding() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(() => {
    if (typeof window === 'undefined') return false;
    return localStorage.getItem(ONBOARDING_STORAGE_KEY) === 'true';
  });

  useEffect(() => {
    if (isComplete) {
      router.push('/dashboard');
    }
  }, [isComplete, router]);

  const nextStep = useCallback(() => {
    setCurrentStep((s) => Math.min(s + 1, TOTAL_STEPS - 1));
  }, []);

  const prevStep = useCallback(() => {
    setCurrentStep((s) => Math.max(s - 1, 0));
  }, []);

  const markComplete = useCallback(() => {
    localStorage.setItem(ONBOARDING_STORAGE_KEY, 'true');
    setIsComplete(true);
    router.push('/dashboard');
  }, [router]);

  return {
    currentStep,
    totalSteps: TOTAL_STEPS,
    isComplete,
    nextStep,
    prevStep,
    skip: markComplete,
    complete: markComplete,
  };
}
