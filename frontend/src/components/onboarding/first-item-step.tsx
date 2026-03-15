'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface FirstItemStepProps {
  onCreated: (title: string) => void;
}

export function FirstItemStep({ onCreated }: FirstItemStepProps) {
  const [title, setTitle] = useState('');

  const handleSubmit = () => {
    const trimmed = title.trim();
    if (trimmed) {
      onCreated(trimmed);
    }
  };

  return (
    <div>
      <h2 className="mb-6 text-center text-2xl font-bold">Create Your First Item</h2>
      <p className="mb-4 text-center text-muted-foreground">
        Try creating an item to see how it works.
      </p>

      <div className="mx-auto max-w-sm space-y-4">
        <div>
          <Label htmlFor="item-title">Title</Label>
          <Input
            id="item-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter a title..."
          />
        </div>
        <Button onClick={handleSubmit} className="w-full">
          Create Item
        </Button>
      </div>
    </div>
  );
}
