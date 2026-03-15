'use client';

import { useOnboarding } from '@/hooks/use-onboarding';
import { WizardContainer, WizardStep } from '@/components/onboarding/wizard-container';
import { WelcomeStep } from '@/components/onboarding/welcome-step';
import { PreferencesStep } from '@/components/onboarding/preferences-step';
import { FirstItemStep } from '@/components/onboarding/first-item-step';
import { CompletionStep } from '@/components/onboarding/completion-step';

export default function OnboardingPage() {
  const { currentStep, isComplete, nextStep, prevStep, skip, complete } = useOnboarding();

  if (isComplete) return null;

  const wizardSteps: WizardStep[] = [
    { label: 'Welcome', content: <WelcomeStep /> },
    { label: 'Preferences', content: <PreferencesStep /> },
    { label: 'First Item', content: <FirstItemStep onCreated={nextStep} /> },
    { label: 'Complete', content: <CompletionStep onFinish={complete} /> },
  ];

  return (
    <WizardContainer
      steps={wizardSteps}
      currentStep={currentStep}
      onNext={currentStep === wizardSteps.length - 1 ? complete : nextStep}
      onBack={prevStep}
      onSkip={skip}
    />
  );
}
