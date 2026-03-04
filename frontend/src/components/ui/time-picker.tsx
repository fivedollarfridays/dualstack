import { type FocusEvent, useState } from 'react';

interface TimePickerProps {
  value: string;
  onChange: (value: string) => void;
  label: string;
  disabled?: boolean;
  className?: string;
}

function validateTime(time: string): { valid: boolean; error?: string } {
  // Check format HH:MM
  const timeRegex = /^(\d{2}):(\d{2})$/;
  const match = time.match(timeRegex);

  if (!match) {
    return { valid: false, error: 'Invalid time format. Use HH:MM (24-hour format)' };
  }

  const [, hourStr, minuteStr] = match;
  const hour = parseInt(hourStr, 10);
  const minute = parseInt(minuteStr, 10);

  if (hour < 0 || hour > 23) {
    return { valid: false, error: 'Invalid time. Hour must be 00-23' };
  }

  if (minute < 0 || minute > 59) {
    return { valid: false, error: 'Invalid time. Minute must be 00-59' };
  }

  return { valid: true };
}

export function TimePicker({
  value,
  onChange,
  label,
  disabled = false,
  className = '',
}: TimePickerProps) {
  const [localValue, setLocalValue] = useState(value);
  const [error, setError] = useState<string | null>(null);

  const handleBlur = (e: FocusEvent<HTMLInputElement>) => {
    const newValue = e.target.value.trim();

    // If value unchanged, do nothing
    if (newValue === value) {
      setError(null);
      return;
    }

    // Validate and update
    const validation = validateTime(newValue);
    if (validation.valid) {
      setError(null);
      onChange(newValue);
    } else {
      setError(validation.error!); // validateTime always returns error when invalid
    }
  };

  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <label
        className={`text-sm font-medium ${
          disabled ? 'text-gray-400' : 'text-gray-200'
        }`}
      >
        {label}
      </label>
      <input
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        onBlur={handleBlur}
        disabled={disabled}
        placeholder="HH:MM"
        aria-invalid={!!error}
        className={`
          px-3 py-2 text-sm border rounded-lg
          ${error ? 'border-red-500' : 'border-gray-600'}
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-gray-700'}
          focus:outline-none focus:ring-2 focus:ring-blue-500
          disabled:text-gray-400
        `}
      />
      {error && (
        <span className="text-xs text-red-600" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
