import React, { useEffect, useRef } from 'react';
import { Textarea } from '@/components/ui/textarea';

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

const MAX_CHARS = 8000;

const PromptInput: React.FC<PromptInputProps> = ({ value, onChange, disabled }) => {
  const ref = useRef<HTMLTextAreaElement>(null);

  // Auto-resize
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(400, Math.max(120, el.scrollHeight))}px`;
  }, [value]);

  return (
    <div className="relative">
      <Textarea
        ref={ref}
        value={value}
        onChange={(e) => onChange(e.target.value.slice(0, MAX_CHARS))}
        disabled={disabled}
        placeholder="Describe your content or paste text here…

Examples:
• 'Generate marketing materials for our Q4 product launch targeting enterprise customers'
• Paste an article, report, advisory, or press release
• 'Create a LinkedIn post and executive summary from this threat intelligence report'"
        className="min-h-[140px] text-sm leading-relaxed"
      />
      <div className="absolute bottom-3 right-3 text-[10px] text-gray-600 pointer-events-none">
        {value.length.toLocaleString()} / {MAX_CHARS.toLocaleString()}
      </div>
    </div>
  );
};

export { PromptInput };
