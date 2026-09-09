import React, { useState } from 'react';
import { ChevronDown, ChevronUp, SlidersHorizontal } from 'lucide-react';
import { Select } from '@/components/ui/select';

const LANGUAGES = [
  { value: 'English', label: 'English' },
  { value: 'Spanish', label: 'Spanish' },
  { value: 'French', label: 'French' },
  { value: 'German', label: 'German' },
  { value: 'Arabic', label: 'Arabic' },
  { value: 'Hindi', label: 'Hindi' },
  { value: 'Portuguese', label: 'Portuguese' },
  { value: 'Chinese', label: 'Chinese' },
  { value: 'Japanese', label: 'Japanese' },
  { value: 'Korean', label: 'Korean' },
];

const TONES = [
  { value: 'Professional', label: 'Professional' },
  { value: 'Conversational', label: 'Conversational' },
  { value: 'Formal', label: 'Formal' },
  { value: 'Casual', label: 'Casual' },
  { value: 'Urgent', label: 'Urgent' },
  { value: 'Inspiring', label: 'Inspiring' },
  { value: 'Technical', label: 'Technical' },
  { value: 'Friendly', label: 'Friendly' },
];

const AUDIENCES = [
  { value: 'General', label: 'General Audience' },
  { value: 'Executives', label: 'Executives / C-Suite' },
  { value: 'Technical', label: 'Technical Teams' },
  { value: 'Marketing', label: 'Marketing Teams' },
  { value: 'Students', label: 'Students' },
  { value: 'Investors', label: 'Investors' },
  { value: 'Public', label: 'General Public' },
];

const DETAIL_LEVELS = [
  { value: 'Brief', label: 'Brief' },
  { value: 'Standard', label: 'Standard' },
  { value: 'Detailed', label: 'Detailed' },
  { value: 'Comprehensive', label: 'Comprehensive' },
];

interface GenerationParamsProps {
  language: string;
  tone: string;
  targetAudience: string;
  detailLevel: string;
  onChange: (field: string, value: string) => void;
  disabled?: boolean;
}

const GenerationParams: React.FC<GenerationParamsProps> = ({
  language, tone, targetAudience, detailLevel, onChange,
}) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-xl border border-white/10 overflow-hidden">
      {/* Header */}
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-3 bg-white/3 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-violet-400" />
          <span className="text-sm font-medium text-gray-200">Advanced Options</span>
          <span className="text-xs text-gray-500">
            {language} · {tone} · {targetAudience}
          </span>
        </div>
        {expanded
          ? <ChevronUp className="w-4 h-4 text-gray-400" />
          : <ChevronDown className="w-4 h-4 text-gray-400" />
        }
      </button>

      {/* Content */}
      {expanded && (
        <div className="p-4 grid grid-cols-2 gap-4 bg-white/2">
          <Select
            label="Language"
            value={language}
            onValueChange={(v) => onChange('language', v)}
            options={LANGUAGES}
          />
          <Select
            label="Tone"
            value={tone}
            onValueChange={(v) => onChange('tone', v)}
            options={TONES}
          />
          <Select
            label="Target Audience"
            value={targetAudience}
            onValueChange={(v) => onChange('target_audience', v)}
            options={AUDIENCES}
          />
          <Select
            label="Detail Level"
            value={detailLevel}
            onValueChange={(v) => onChange('detail_level', v)}
            options={DETAIL_LEVELS}
          />
        </div>
      )}
    </div>
  );
};

export { GenerationParams };
