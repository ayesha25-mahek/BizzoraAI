import * as React from 'react';
import { cn } from '@/lib/utils';

const Textarea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        'flex min-h-[120px] w-full rounded-lg border border-white/10 bg-white/5',
        'px-4 py-3 text-sm text-gray-100 placeholder:text-gray-500',
        'focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/50',
        'disabled:cursor-not-allowed disabled:opacity-50 resize-none transition-all duration-150',
        className
      )}
      {...props}
    />
  )
);
Textarea.displayName = 'Textarea';

export { Textarea };
