export type OutputFormat =
  | 'video'
  | 'linkedin'
  | 'twitter'
  | 'presentation'
  | 'advisory'
  | 'executive_summary'
  | 'infographic'
  | 'article';

export interface OutputFormatMeta {
  id: OutputFormat;
  label: string;
  description: string;
  icon: string;
  estimatedTime: string;
  badge?: string;
}

export interface GenerationParams {
  prompt: string;
  files: File[];
  outputs: OutputFormat[];
  language: string;
  tone: string;
  target_audience: string;
  detail_level: string;
}

export interface ProgressEvent {
  stage: string;
  message: string;
  percent: number;
  current?: string;
}

export interface ResultEvent {
  output_type: OutputFormat;
  status: 'success' | 'error' | 'not_implemented';
  content: string;
  download_url?: string;
  filename?: string;
}

export interface GenerationState {
  status: 'idle' | 'generating' | 'complete' | 'error';
  progress: ProgressEvent | null;
  results: Partial<Record<OutputFormat, ResultEvent>>;
  error: string | null;
}
