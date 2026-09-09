import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-violet-500/50 disabled:pointer-events-none disabled:opacity-40 active:scale-95',
  {
    variants: {
      variant: {
        default:
          'bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-lg shadow-violet-500/20 hover:shadow-violet-500/30',
        outline:
          'border border-white/20 bg-transparent text-gray-200 hover:bg-white/5 hover:border-white/30',
        ghost:
          'bg-transparent text-gray-300 hover:bg-white/5 hover:text-white',
        destructive:
          'bg-red-600/20 border border-red-500/30 text-red-300 hover:bg-red-600/30',
        secondary:
          'bg-white/10 text-gray-200 hover:bg-white/15 border border-white/10',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        default: 'h-10 px-4 py-2 text-sm',
        lg: 'h-12 px-6 text-base',
        xl: 'h-14 px-8 text-lg',
        icon: 'h-9 w-9 p-0',
      },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  )
);
Button.displayName = 'Button';

export { Button, buttonVariants };
