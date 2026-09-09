import React, { useCallback, useRef, useState } from 'react';
import { Upload, X } from 'lucide-react';
import { cn, formatFileSize, getFileIcon } from '@/lib/utils';

const ACCEPTED = '.pdf,.docx,.pptx,.txt,.png,.jpg,.jpeg,.webp,.mp4,.mov,.avi';
const MAX_FILES = 10;

function getTypeColor(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() ?? '';
  if (['pdf', 'docx', 'pptx', 'txt'].includes(ext)) return 'text-violet-400';
  if (['png', 'jpg', 'jpeg', 'webp', 'gif'].includes(ext)) return 'text-blue-400';
  if (['mp4', 'mov', 'avi'].includes(ext)) return 'text-orange-400';
  return 'text-gray-400';
}

interface FileUploadZoneProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
  disabled?: boolean;
}

const FileUploadZone: React.FC<FileUploadZoneProps> = ({ files, onFilesChange, disabled }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const addFiles = useCallback(
    (newFiles: FileList | null) => {
      if (!newFiles) return;
      const arr = Array.from(newFiles);
      const combined = [...files, ...arr].slice(0, MAX_FILES);
      onFilesChange(combined);
    },
    [files, onFilesChange]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      if (!disabled) addFiles(e.dataTransfer.files);
    },
    [addFiles, disabled]
  );

  const removeFile = (index: number) => {
    onFilesChange(files.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-3">
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); if (!disabled) setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => !disabled && inputRef.current?.click()}
        className={cn(
          'relative rounded-xl border-2 border-dashed p-8 text-center cursor-pointer transition-all duration-200',
          dragging
            ? 'border-violet-500 bg-violet-500/10 glow-violet'
            : 'border-white/15 bg-white/3 hover:border-white/25 hover:bg-white/5',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept={ACCEPTED}
          className="hidden"
          onChange={(e) => addFiles(e.target.files)}
          disabled={disabled}
        />

        <div className={cn(
          'w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3 transition-colors',
          dragging ? 'bg-violet-600/30' : 'bg-white/10'
        )}>
          <Upload className={cn('w-5 h-5', dragging ? 'text-violet-300' : 'text-gray-400')} />
        </div>

        <p className="text-sm font-medium text-gray-200 mb-1">
          {dragging ? 'Drop files here' : 'Drag & drop files here'}
        </p>
        <p className="text-xs text-gray-500 mb-2">or click to browse</p>
        <p className="text-[11px] text-gray-600">
          PDF, DOCX, PPTX, TXT, PNG, JPG, MP4 · Max {MAX_FILES} files
        </p>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, i) => (
            <div
              key={`${file.name}-${i}`}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-white/5 border border-white/10 group"
            >
              <span className={cn('text-base leading-none', getTypeColor(file.name))}>
                {getFileIcon(file.name)}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-gray-200 truncate">{file.name}</p>
                <p className="text-[10px] text-gray-500">{formatFileSize(file.size)}</p>
              </div>
              <button
                type="button"
                onClick={() => removeFile(i)}
                className="w-6 h-6 rounded-md flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/10 text-gray-400 hover:text-red-400"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {files.length >= MAX_FILES && (
        <p className="text-xs text-amber-400">Maximum {MAX_FILES} files reached.</p>
      )}
    </div>
  );
};

export { FileUploadZone };
