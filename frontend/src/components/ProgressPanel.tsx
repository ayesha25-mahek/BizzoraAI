import React from 'react';
import { Brain, Zap, FileSearch, CheckCircle2, Sparkles, Loader2 } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import type { ProgressEvent, ResultEvent, OutputFormat } from '@/types';
import { OUTPUT_FORMATS } from '@/components/OutputFormatSelector';

const STAGE_ICONS: Record<string, React.FC<{ className?: string }>> = {
  reading: FileSearch,
  analyzing: Brain,
  preparing: Sparkles,
  generating: Zap,
  done: CheckCircle2,
};

interface ProgressPanelProps {
  progress: ProgressEvent | null;
  completedResults: Partial<Record<OutputFormat, ResultEvent>>;
  selectedOutputs: OutputFormat[];
}

const ProgressPanel: React.FC<ProgressPanelProps> = ({ progress, completedResults, selectedOutputs }) => {
  const stage = progress?.stage ?? 'analyzing';
  const StageIcon = STAGE_ICONS[stage] ?? Zap;
  const percent = progress?.percent ?? 0;
  const message = progress?.message ?? 'Processing…';

  return (
    <div className="rounded-xl border border-violet-500/20 bg-gradient-to-br from-violet-950/30 to-indigo-950/20 p-6 space-y-5">
      {/* Stage indicator */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <div className="w-10 h-10 rounded-full bg-violet-600/20 flex items-center justify-center">
            <StageIcon className="w-5 h-5 text-violet-400" />
          </div>
          {stage !== 'done' && (
            <div className="absolute inset-0 rounded-full border-2 border-violet-500/40 animate-ping" />
          )}
        </div>
        <div>
          <p className="text-sm font-semibold text-violet-200">{message}</p>
          <p className="text-xs text-gray-500 capitalize">{stage === 'done' ? 'Complete' : 'BizzoraAI is working…'}</p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="space-y-1.5">
        <Progress value={percent} />
        <div className="flex justify-between text-[10px] text-gray-500">
          <span>Processing</span>
          <span>{percent}%</span>
        </div>
      </div>

      {/* Output status list */}
      {selectedOutputs.length > 0 && (
        <div className="space-y-2">
          {selectedOutputs.map((outputId) => {
            const meta = OUTPUT_FORMATS.find((f) => f.id === outputId);
            const result = completedResults[outputId];
            const isDone = !!result;
            const isError = result?.status === 'error';
            const isCurrent = progress?.current === outputId;

            return (
              <div
                key={outputId}
                className={cn(
                  'flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs transition-all duration-300',
                  isDone && !isError ? 'bg-emerald-500/10 border border-emerald-500/20' :
                  isError ? 'bg-red-500/10 border border-red-500/20' :
                  isCurrent ? 'bg-violet-500/10 border border-violet-500/20' :
                  'bg-white/3 border border-white/8'
                )}
              >
                {isDone && !isError ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                ) : isCurrent ? (
                  <Loader2 className="w-3.5 h-3.5 text-violet-400 animate-spin shrink-0" />
                ) : (
                  <div className={cn('w-3.5 h-3.5 rounded-full border shrink-0',
                    isError ? 'border-red-400' : 'border-white/20'
                  )} />
                )}
                <span className={cn(
                  'font-medium',
                  isDone && !isError ? 'text-emerald-300' :
                  isError ? 'text-red-300' :
                  isCurrent ? 'text-violet-200' : 'text-gray-500'
                )}>
                  {meta?.label ?? outputId}
                </span>
                {isError && <span className="text-red-400 ml-auto">Failed</span>}
                {isDone && !isError && <span className="text-emerald-400 ml-auto">Done</span>}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export { ProgressPanel };
