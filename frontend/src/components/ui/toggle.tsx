import { type KeyboardEvent } from 'react';

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  ariaLabel?: string;
  disabled?: boolean;
  className?: string;
}

export function Toggle({
  checked,
  onChange,
  label,
  ariaLabel,
  disabled = false,
  className = '',
}: ToggleProps) {
  const handleClick = () => {
    if (!disabled) {
      onChange(!checked);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (disabled) return;

    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      onChange(!checked);
    }
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div
        role="switch"
        aria-checked={checked}
        aria-label={ariaLabel || label}
        aria-disabled={disabled}
        tabIndex={disabled ? -1 : 0}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        className={`
          relative inline-flex h-6 w-11 items-center rounded-full
          transition-colors duration-200 ease-in-out
          ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
          ${checked ? 'bg-blue-600' : 'bg-gray-600'}
        `}
      >
        <span
          className={`
            inline-block h-4 w-4 transform rounded-full bg-white
            transition-transform duration-200 ease-in-out
            ${checked ? 'translate-x-6' : 'translate-x-1'}
          `}
        />
      </div>
      {label && (
        <label
          className={`
            text-sm font-medium text-gray-200
            ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
          `}
          onClick={handleClick}
        >
          {label}
        </label>
      )}
    </div>
  );
}
