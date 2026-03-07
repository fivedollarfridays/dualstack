import * as React from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('rounded-lg border border-gray-700 bg-gray-800 p-6', className)}
      {...props}
    >
      {children}
    </div>
  )
);
Card.displayName = 'Card';

export { Card };
