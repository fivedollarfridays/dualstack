import { type ChangeEvent, type KeyboardEvent } from 'react';
import { cn } from '@/lib/utils';

interface SliderProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  label?: string;
  showValue?: boolean;
  valueFormatter?: (value: number) => string;
  className?: string;
  'aria-label'?: string;
}

export function Slider({
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  disabled = false,
  label,
  showValue = false,
  valueFormatter,
  className,
  'aria-label': ariaLabel,
}: SliderProps) {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (!disabled) {
      onChange(parseFloat(e.target.value));
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (disabled) return;

    let newValue = value;

    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowUp':
        newValue = Math.min(max, value + step);
        break;
      case 'ArrowLeft':
      case 'ArrowDown':
        newValue = Math.max(min, value - step);
        break;
      default:
        return;
    }

    if (newValue !== value) {
      e.preventDefault();
      onChange(newValue);
    }
  };

  const displayValue = valueFormatter ? valueFormatter(value) : String(value);
  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div
      className={cn(
        'flex flex-col gap-2',
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
    >
      {label && (
        <label className="text-sm font-medium text-gray-200">{label}</label>
      )}
      <div className="flex items-center gap-3">
        <input
          type="range"
          role="slider"
          value={value}
          min={min}
          max={max}
          step={step}
          disabled={disabled}
          aria-label={ariaLabel || label}
          onChange={handleChange}
          onInput={handleChange}
          onKeyDown={handleKeyDown}
          className={cn(
            'w-full h-2 rounded-lg appearance-none cursor-pointer',
            'bg-gray-600',
            '[&::-webkit-slider-thumb]:appearance-none',
            '[&::-webkit-slider-thumb]:w-4',
            '[&::-webkit-slider-thumb]:h-4',
            '[&::-webkit-slider-thumb]:rounded-full',
            '[&::-webkit-slider-thumb]:bg-purple-500',
            '[&::-webkit-slider-thumb]:hover:bg-purple-400',
            '[&::-webkit-slider-thumb]:cursor-pointer',
            '[&::-webkit-slider-thumb]:transition-colors',
            '[&::-moz-range-thumb]:w-4',
            '[&::-moz-range-thumb]:h-4',
            '[&::-moz-range-thumb]:rounded-full',
            '[&::-moz-range-thumb]:bg-purple-500',
            '[&::-moz-range-thumb]:hover:bg-purple-400',
            '[&::-moz-range-thumb]:border-0',
            '[&::-moz-range-thumb]:cursor-pointer',
            'focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-900',
            disabled && 'cursor-not-allowed'
          )}
          style={{
            background: `linear-gradient(to right, #a855f7 0%, #a855f7 ${percentage}%, #4b5563 ${percentage}%, #4b5563 100%)`,
          }}
        />
        {showValue && (
          <span className="text-sm font-medium text-gray-200 min-w-[3rem] text-right">
            {displayValue}
          </span>
        )}
      </div>
    </div>
  );
}
