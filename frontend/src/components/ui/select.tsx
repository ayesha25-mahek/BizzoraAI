import * as React from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps {
  value: string;
  onValueChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
  className?: string;
  label?: string;
}

const Select: React.FC<SelectProps> = ({
  value,
  onValueChange,
  options,
  placeholder = 'Select…',
  className,
  label,
}) => {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">{label}</label>}
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onValueChange(e.target.value)}
          className={cn(
            'w-full appearance-none rounded-lg border border-white/10 bg-white/5',
            'px-3 py-2.5 pr-8 text-sm text-gray-100',
            'focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/50',
            'cursor-pointer transition-all duration-150',
            className
          )}
        >
          {placeholder && (
            <option value="" disabled className="bg-[#1A1A24] text-gray-400">
              {placeholder}
            </option>
          )}
          {options.map((opt) => (
            <option key={opt.value} value={opt.value} className="bg-[#1A1A24] text-gray-100">
              {opt.label}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
      </div>
    </div>
  );
};

export { Select };
export type { SelectOption };
