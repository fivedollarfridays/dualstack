'use client';

import { ReactNode } from 'react';
import { Button } from '@/components/ui/button';

export interface WizardStep {
  label: string;
  content: ReactNode;
}

interface WizardContainerProps {
  steps: WizardStep[];
  currentStep: number;
  onNext: () => void;
  onBack: () => void;
  onSkip: () => void;
}

export function WizardContainer({
  steps,
  currentStep,
  onNext,
  onBack,
  onSkip,
}: WizardContainerProps) {
  const isLastStep = currentStep === steps.length - 1;
  const isFirstStep = currentStep === 0;

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="mb-6 text-center text-sm text-muted-foreground">
        Step {currentStep + 1} of {steps.length}
      </div>

      <div className="mb-4 flex gap-1">
        {steps.map((_, i) => (
          <div
            key={i}
            className={`h-1.5 flex-1 rounded-full ${
              i <= currentStep ? 'bg-primary' : 'bg-muted'
            }`}
          />
        ))}
      </div>

      <div className="min-h-[300px]">{steps[currentStep].content}</div>

      <div className="mt-8 flex items-center justify-between">
        <Button variant="ghost" onClick={onSkip}>
          Skip
        </Button>

        <div className="flex gap-2">
          {!isFirstStep && (
            <Button variant="outline" onClick={onBack}>
              Back
            </Button>
          )}
          {isLastStep ? (
            <Button onClick={onNext}>Finish</Button>
          ) : (
            <Button onClick={onNext}>Next</Button>
          )}
        </div>
      </div>
    </div>
  );
}
