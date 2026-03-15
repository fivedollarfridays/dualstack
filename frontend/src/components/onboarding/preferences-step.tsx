'use client';

import { useState } from 'react';
import { Label } from '@/components/ui/label';

export function PreferencesStep() {
  const [theme, setTheme] = useState('light');
  const [notifications, setNotifications] = useState(false);

  return (
    <div>
      <h2 className="mb-6 text-center text-2xl font-bold">Set Your Preferences</h2>

      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Label htmlFor="theme">Theme</Label>
          <select
            id="theme"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="rounded-md border px-3 py-1.5 text-sm"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System</option>
          </select>
        </div>

        <div className="flex items-center justify-between">
          <Label htmlFor="notifications">Notifications</Label>
          <input
            type="checkbox"
            id="notifications"
            checked={notifications}
            onChange={(e) => setNotifications(e.target.checked)}
            className="h-4 w-4 rounded border"
          />
        </div>
      </div>
    </div>
  );
}
