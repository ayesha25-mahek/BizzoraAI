import React, { useState } from 'react';
import {
  Copy, Download, CheckCheck, FileText, Video, Linkedin,
  Twitter, Presentation, BarChart2, Layout, PenTool, AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { downloadFile } from '@/lib/api';
import type { ResultEvent, OutputFormat } from '@/types';
import { OUTPUT_FORMATS } from '@/components/OutputFormatSelector';

const ICON_MAP: Record<string, React.FC<{ className?: string }>> = {
  Video, Linkedin, Twitter, Presentation, FileText, BarChart2, Layout, PenTool,
};

interface ResultCardProps {
  result: ResultEvent;
  index: number;
}

const ResultCard: React.FC<ResultCardProps> = ({ result, index }) => {
  const [copied, setCopied] = useState(false);
  const meta = OUTPUT_FORMATS.find((f) => f.id === result.output_type);
  const IconComponent = ICON_MAP[meta?.icon ?? 'FileText'] ?? FileText;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(result.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback
    }
  };

  const handleDownload = () => {
    if (result.download_url) {
      downloadFile(result.download_url, result.filename);
    }
  };

  const isError = result.status === 'error';
  const hasDownload = !!result.download_url;
  const hasText = !!result.content;

  // Format content as markdown-ish for readability
  const formattedContent = result.content
    .replace(/^#{1,3} (.+)$/gm, (_, t) => `\n${t.toUpperCase()}\n`)
    .replace(/^\*\*(.+)\*\*$/gm, (_, t) => `${t}`)
    .replace(/^- /gm, '• ');

  return (
    <div
      className={cn(
        'rounded-xl border bg-white/5 backdrop-blur-md flex flex-col',
        'animate-in fade-in slide-in-from-bottom-2 duration-300',
        isError ? 'border-red-500/30' : 'border-white/10',
      )}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      {/* Header */}
      <div className="flex items-center gap-3 p-4 pb-3 border-b border-white/8">
        <div className={cn(
          'w-8 h-8 rounded-lg flex items-center justify-center shrink-0',
          isError ? 'bg-red-500/20' : 'bg-violet-600/20'
        )}>
          {isError
            ? <AlertCircle className="w-4 h-4 text-red-400" />
            : <IconComponent className="w-4 h-4 text-violet-300" />
          }
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-gray-100 truncate">
              {meta?.label ?? result.output_type}
            </h3>
            <Badge variant={isError ? 'destructive' : 'success'} className="text-[10px] shrink-0">
              {isError ? 'Error' : 'Generated'}
            </Badge>
          </div>
          <p className="text-[10px] text-gray-500">{meta?.estimatedTime}</p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1.5 shrink-0">
          {hasText && !isError && (
            <Button variant="ghost" size="icon" onClick={handleCopy} title="Copy to clipboard"
              className="w-7 h-7 text-gray-400 hover:text-gray-100">
              {copied ? <CheckCheck className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            </Button>
          )}
          {hasDownload && (
            <Button variant="ghost" size="icon" onClick={handleDownload} title="Download file"
              className="w-7 h-7 text-gray-400 hover:text-violet-300">
              <Download className="w-3.5 h-3.5" />
            </Button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-4 overflow-hidden">
        {isError ? (
          <p className="text-sm text-red-300">{result.content}</p>
        ) : hasDownload ? (
          <div className="space-y-3">
            <p className="text-sm text-gray-300">{result.content}</p>
            <Button onClick={handleDownload} size="sm" className="w-full gap-2">
              <Download className="w-3.5 h-3.5" />
              Download {result.filename ?? 'File'}
            </Button>
          </div>
        ) : (
          <pre className="text-xs text-gray-300 whitespace-pre-wrap font-sans leading-relaxed max-h-72 overflow-y-auto custom-scroll">
            {formattedContent}
          </pre>
        )}
      </div>
    </div>
  );
};

interface ResultsPanelProps {
  results: Partial<Record<OutputFormat, ResultEvent>>;
  onDownloadAll: () => void;
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ results, onDownloadAll }) => {
  const entries = Object.values(results).filter(Boolean) as ResultEvent[];
  const hasDownloadable = entries.some((r) => r.download_url);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-base font-bold text-white">Generated Content</span>
          <Badge variant="success">{entries.length} output{entries.length !== 1 ? 's' : ''}</Badge>
        </div>
        {hasDownloadable && (
          <Button variant="outline" size="sm" onClick={onDownloadAll} className="gap-1.5">
            <Download className="w-3.5 h-3.5" />
            Download All
          </Button>
        )}
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {entries.map((result, i) => (
          <ResultCard key={result.output_type} result={result} index={i} />
        ))}
      </div>
    </div>
  );
};

export { ResultsPanel };
