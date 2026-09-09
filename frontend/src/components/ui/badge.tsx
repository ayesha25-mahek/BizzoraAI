import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-violet-600/20 text-violet-300 border border-violet-500/30',
        success: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
        warning: 'bg-amber-500/20 text-amber-300 border border-amber-500/30',
        destructive: 'bg-red-500/20 text-red-300 border border-red-500/30',
        outline: 'border border-white/20 text-gray-300',
        blue: 'bg-blue-500/20 text-blue-300 border border-blue-500/30',
      },
    },
    defaultVariants: { variant: 'default' },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
