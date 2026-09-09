import type { OutputFormat, ProgressEvent, ResultEvent } from '@/types';

const API_BASE = '/api';

export interface GenerateCallbacks {
  onProgress: (event: ProgressEvent) => void;
  onResult: (event: ResultEvent) => void;
  onDone: () => void;
  onError: (message: string) => void;
}

/**
 * Generate content via SSE stream from the backend.
 * Uses fetch + ReadableStream to handle server-sent events.
 */
export async function generateContent(
  formData: FormData,
  callbacks: GenerateCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const { onProgress, onResult, onDone, onError } = callbacks;

  try {
    const response = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      body: formData,
      signal,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Server error ${response.status}: ${text}`);
    }

    if (!response.body) {
      throw new Error('No response body received');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Parse SSE events from buffer
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? ''; // keep incomplete line

      let currentEvent = '';
      let currentData = '';

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim();
        } else if (line.startsWith('data: ')) {
          currentData = line.slice(6).trim();
        } else if (line === '') {
          // End of event block
          if (currentEvent && currentData) {
            try {
              const parsed = JSON.parse(currentData);
              switch (currentEvent) {
                case 'progress':
                  onProgress(parsed as ProgressEvent);
                  break;
                case 'result':
                  onResult(parsed as ResultEvent);
                  break;
                case 'done':
                  onDone();
                  break;
                case 'error':
                  onError((parsed as { message: string }).message ?? 'Unknown error');
                  break;
              }
            } catch {
              // ignore parse errors on individual events
            }
            currentEvent = '';
            currentData = '';
          }
        }
      }
    }
  } catch (err: unknown) {
    if (err instanceof Error && err.name === 'AbortError') {
      return; // cancelled by user
    }
    const message = err instanceof Error ? err.message : 'Network error occurred';
    onError(message);
  }
}

/**
 * Download a file from the backend.
 */
export function downloadFile(url: string, filename?: string): void {
  const a = document.createElement('a');
  a.href = url;
  if (filename) a.download = filename;
  a.target = '_blank';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/**
 * Download all available files.
 */
export function downloadAllFiles(
  results: Partial<Record<OutputFormat, ResultEvent>>
): void {
  Object.values(results).forEach((result) => {
    if (result?.download_url) {
      setTimeout(() => {
        downloadFile(result.download_url!, result.filename);
      }, 100);
    }
  });
}

/**
 * Check backend health.
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`, { method: 'GET' });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Fetch available output types from backend.
 */
export async function fetchOutputTypes(): Promise<string[]> {
  try {
    const response = await fetch(`${API_BASE}/outputs`);
    if (!response.ok) return [];
    const data = await response.json();
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}
