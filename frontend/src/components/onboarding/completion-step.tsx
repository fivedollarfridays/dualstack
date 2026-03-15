'use client';

import { Button } from '@/components/ui/button';

interface CompletionStepProps {
  onFinish: () => void;
}

export function CompletionStep({ onFinish }: CompletionStepProps) {
  return (
    <div className="text-center">
      <h2 className="mb-4 text-2xl font-bold">You&apos;re All Set!</h2>
      <p className="mb-6 text-muted-foreground">
        Your workspace is ready. Start building something great.
      </p>
      <Button onClick={onFinish}>Go to Dashboard</Button>
    </div>
  );
}
