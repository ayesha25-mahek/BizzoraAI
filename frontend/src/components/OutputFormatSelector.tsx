import React from 'react';
import {
  Video, Linkedin, Twitter, Presentation, FileText,
  BarChart2, Layout, PenTool, Check
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import type { OutputFormat, OutputFormatMeta } from '@/types';

const OUTPUT_FORMATS: OutputFormatMeta[] = [
  {
    id: 'linkedin',
    label: 'LinkedIn Post',
    description: 'Professional post ready to publish',
    icon: 'Linkedin',
    estimatedTime: '~30 sec',
    badge: 'Popular',
  },
  {
    id: 'twitter',
    label: 'Twitter/X Post',
    description: 'Optimised tweets or thread',
    icon: 'Twitter',
    estimatedTime: '~20 sec',
  },
  {
    id: 'executive_summary',
    label: 'Executive Summary',
    description: 'Concise C-suite briefing',
    icon: 'BarChart2',
    estimatedTime: '~30 sec',
    badge: 'Popular',
  },
  {
    id: 'presentation',
    label: 'Presentation',
    description: 'PPTX slides with speaker notes',
    icon: 'Presentation',
    estimatedTime: '~1 min',
  },
  {
    id: 'advisory',
    label: 'Advisory Document',
    description: 'Structured advisory with recommendations',
    icon: 'FileText',
    estimatedTime: '~45 sec',
    badge: 'New',
  },
  {
    id: 'infographic',
    label: 'Infographic',
    description: 'Key messaging & layout guide',
    icon: 'Layout',
    estimatedTime: '~45 sec',
  },
  {
    id: 'article',
    label: 'Article',
    description: 'Full-length article or blog post',
    icon: 'PenTool',
    estimatedTime: '~1 min',
  },
  {
    id: 'video',
    label: 'AI Video Package',
    description: 'Script, storyboard & narration',
    icon: 'Video',
    estimatedTime: '3–5 min',
    badge: 'AI Video',
  },
];

const ICON_MAP: Record<string, React.FC<{ className?: string }>> = {
  Video,
  Linkedin,
  Twitter,
  Presentation,
  FileText,
  BarChart2,
  Layout,
  PenTool,
};

interface OutputFormatCardProps {
  format: OutputFormatMeta;
  selected: boolean;
  onToggle: (id: OutputFormat) => void;
  disabled?: boolean;
}

const OutputFormatCard: React.FC<OutputFormatCardProps> = ({ format, selected, onToggle, disabled }) => {
  const IconComponent = ICON_MAP[format.icon] ?? FileText;

  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => onToggle(format.id)}
      className={cn(
        'relative group w-full text-left rounded-xl border p-4 transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-violet-500/50',
        'hover:scale-[1.02]',
        selected
          ? 'border-violet-500/60 bg-violet-600/10 shadow-lg shadow-violet-500/15 selected-card-border'
          : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/8 hover:shadow-md hover:shadow-violet-500/5',
        disabled && 'opacity-50 cursor-not-allowed hover:scale-100'
      )}
    >
      {/* Selected checkmark */}
      {selected && (
        <div className="absolute top-3 right-3 w-5 h-5 rounded-full bg-violet-600 flex items-center justify-center">
          <Check className="w-3 h-3 text-white" />
        </div>
      )}

      {/* Icon */}
      <div className={cn(
        'w-9 h-9 rounded-lg flex items-center justify-center mb-3 transition-colors',
        selected ? 'bg-violet-600/30' : 'bg-white/10 group-hover:bg-white/15'
      )}>
        <IconComponent className={cn('w-4.5 h-4.5', selected ? 'text-violet-300' : 'text-gray-300')} />
      </div>

      {/* Label */}
      <div className="flex items-center gap-2 mb-1">
        <span className={cn('text-sm font-semibold', selected ? 'text-violet-200' : 'text-gray-100')}>
          {format.label}
        </span>
        {format.badge && (
          <Badge variant={format.badge === 'Popular' ? 'default' : format.badge === 'AI Video' ? 'blue' : 'warning'}
            className="text-[10px] px-1.5 py-0">
            {format.badge}
          </Badge>
        )}
      </div>

      {/* Description */}
      <p className="text-xs text-gray-400 leading-relaxed mb-2">{format.description}</p>

      {/* Estimated time */}
      <span className="text-[10px] text-gray-500">{format.estimatedTime}</span>
    </button>
  );
};

interface OutputFormatSelectorProps {
  selected: OutputFormat[];
  onToggle: (id: OutputFormat) => void;
  disabled?: boolean;
}

const OutputFormatSelector: React.FC<OutputFormatSelectorProps> = ({ selected, onToggle, disabled }) => {
  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-200">Select Output Formats</h3>
        {selected.length > 0 && (
          <span className="text-xs text-violet-400">{selected.length} selected</span>
        )}
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {OUTPUT_FORMATS.map((format) => (
          <OutputFormatCard
            key={format.id}
            format={format}
            selected={selected.includes(format.id)}
            onToggle={onToggle}
            disabled={disabled}
          />
        ))}
      </div>
    </div>
  );
};

export { OutputFormatSelector, OUTPUT_FORMATS };
