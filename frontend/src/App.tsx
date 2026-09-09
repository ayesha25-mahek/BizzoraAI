import { useRef, useState } from 'react';
import { Sparkles, X, Loader2, RotateCcw, FileText } from 'lucide-react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { PromptInput } from '@/components/PromptInput';
import { FileUploadZone } from '@/components/FileUploadZone';
import { OutputFormatSelector } from '@/components/OutputFormatSelector';
import { GenerationParams } from '@/components/GenerationParams';
import { ProgressPanel } from '@/components/ProgressPanel';
import { ResultsPanel } from '@/components/ResultsPanel';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { generateContent, downloadAllFiles } from '@/lib/api';
import type {
  OutputFormat, GenerationState, ProgressEvent as PEvt, ResultEvent
} from '@/types';

const INITIAL_STATE: GenerationState = {
  status: 'idle',
  progress: null,
  results: {},
  error: null,
};

function App() {
  // Form state
  const [prompt, setPrompt] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [selectedOutputs, setSelectedOutputs] = useState<OutputFormat[]>([]);
  const [language, setLanguage] = useState('English');
  const [tone, setTone] = useState('Professional');
  const [targetAudience, setTargetAudience] = useState('General');
  const [detailLevel, setDetailLevel] = useState('Standard');

  // Generation state
  const [genState, setGenState] = useState<GenerationState>(INITIAL_STATE);
  const abortRef = useRef<AbortController | null>(null);

  const isGenerating = genState.status === 'generating';
  const canGenerate =
    !isGenerating &&
    selectedOutputs.length > 0 &&
    (prompt.trim().length > 0 || files.length > 0);

  const toggleOutput = (id: OutputFormat) => {
    setSelectedOutputs((prev) =>
      prev.includes(id) ? prev.filter((o) => o !== id) : [...prev, id]
    );
  };

  const handleParamChange = (field: string, value: string) => {
    if (field === 'language') setLanguage(value);
    else if (field === 'tone') setTone(value);
    else if (field === 'target_audience') setTargetAudience(value);
    else if (field === 'detail_level') setDetailLevel(value);
  };

  const handleGenerate = async () => {
    if (!canGenerate) return;

    // Build multipart form
    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('outputs', JSON.stringify(selectedOutputs));
    formData.append('language', language);
    formData.append('tone', tone);
    formData.append('target_audience', targetAudience);
    formData.append('detail_level', detailLevel);
    files.forEach((f) => formData.append('files', f));

    // Reset state
    const controller = new AbortController();
    abortRef.current = controller;
    setGenState({ status: 'generating', progress: null, results: {}, error: null });

    await generateContent(formData, {
      onProgress: (event: PEvt) => {
        setGenState((prev) => ({ ...prev, progress: event }));
      },
      onResult: (event: ResultEvent) => {
        setGenState((prev) => ({
          ...prev,
          results: { ...prev.results, [event.output_type]: event },
        }));
      },
      onDone: () => {
        setGenState((prev) => ({ ...prev, status: 'complete' }));
      },
      onError: (message: string) => {
        setGenState((prev) => ({ ...prev, status: 'error', error: message }));
      },
    }, controller.signal);
  };

  const handleStop = () => {
    abortRef.current?.abort();
    setGenState((prev) => ({ ...prev, status: 'idle' }));
  };

  const handleReset = () => {
    abortRef.current?.abort();
    setGenState(INITIAL_STATE);
  };

  const showResults =
    genState.status === 'complete' || Object.keys(genState.results).length > 0;

  return (
    <div className="min-h-screen flex flex-col bg-[#0A0A0F]">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-8">
        {/* Page heading */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
            Transform Your{' '}
            <span className="gradient-text">Content</span>
          </h1>
          <p className="text-gray-400 max-w-2xl text-sm leading-relaxed">
            Upload documents, paste text, or describe your content. Select desired output formats
            and let BizzoraAI generate professional deliverables instantly.
          </p>
        </div>

        {/* Main 2-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-8 items-start">

          {/* ─── LEFT COLUMN: Input ─────────────────────────────────── */}
          <div className="space-y-6">

            {/* Prompt */}
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-200 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-violet-400" />
                Source Content
              </label>
              <PromptInput
                value={prompt}
                onChange={setPrompt}
                disabled={isGenerating}
              />
            </div>

            {/* File upload */}
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-200">
                Upload Files{' '}
                <span className="text-gray-500 font-normal">(optional)</span>
              </label>
              <FileUploadZone
                files={files}
                onFilesChange={setFiles}
                disabled={isGenerating}
              />
            </div>

            <Separator />

            {/* Advanced options */}
            <GenerationParams
              language={language}
              tone={tone}
              targetAudience={targetAudience}
              detailLevel={detailLevel}
              onChange={handleParamChange}
              disabled={isGenerating}
            />

            {/* Output format selector */}
            <OutputFormatSelector
              selected={selectedOutputs}
              onToggle={toggleOutput}
              disabled={isGenerating}
            />

            {/* Error banner */}
            {genState.status === 'error' && genState.error && (
              <div className="flex items-start gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/30">
                <X className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-medium text-red-300">Generation failed</p>
                  <p className="text-xs text-red-400 mt-0.5">{genState.error}</p>
                </div>
              </div>
            )}

            {/* Generate / Stop button */}
            <div className="flex gap-3">
              {isGenerating ? (
                <>
                  <Button
                    onClick={handleStop}
                    variant="outline"
                    size="lg"
                    className="flex-1 gap-2"
                  >
                    <X className="w-4 h-4" />
                    Stop
                  </Button>
                  <Button size="lg" disabled className="flex-1 gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating…
                  </Button>
                </>
              ) : (
                <>
                  {genState.status !== 'idle' && (
                    <Button variant="outline" size="lg" onClick={handleReset} className="gap-2">
                      <RotateCcw className="w-4 h-4" />
                      Reset
                    </Button>
                  )}
                  <Button
                    size="lg"
                    onClick={handleGenerate}
                    disabled={!canGenerate}
                    className="flex-1 gap-2 text-base"
                  >
                    <Sparkles className="w-5 h-5" />
                    Generate{selectedOutputs.length > 0 ? ` ${selectedOutputs.length} Output${selectedOutputs.length > 1 ? 's' : ''}` : ''}
                  </Button>
                </>
              )}
            </div>
          </div>

          {/* ─── RIGHT COLUMN: Progress / Results ───────────────────── */}
          <div className="space-y-6">

            {/* Idle placeholder */}
            {genState.status === 'idle' && !showResults && (
              <div className="rounded-xl border border-white/8 bg-white/3 p-8 text-center">
                <div className="w-16 h-16 rounded-2xl bg-violet-600/10 border border-violet-500/20 flex items-center justify-center mx-auto mb-4">
                  <FileText className="w-7 h-7 text-violet-400" />
                </div>
                <h3 className="text-sm font-semibold text-gray-300 mb-1">
                  Your generated content will appear here
                </h3>
                <p className="text-xs text-gray-600 leading-relaxed">
                  Select output formats, add your content, and click Generate to get started.
                </p>

                {/* Quick tips */}
                <div className="mt-6 space-y-2 text-left">
                  {[
                    'Supports PDF, DOCX, PPTX, TXT and image files',
                    'Select multiple output formats at once',
                    'Configure language, tone & target audience',
                    'Download outputs as files or copy to clipboard',
                  ].map((tip, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-gray-600">
                      <div className="w-1.5 h-1.5 rounded-full bg-violet-600 shrink-0" />
                      {tip}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Progress panel */}
            {isGenerating && (
              <ProgressPanel
                progress={genState.progress}
                completedResults={genState.results}
                selectedOutputs={selectedOutputs}
              />
            )}

            {/* Results */}
            {showResults && (
              <ResultsPanel
                results={genState.results}
                onDownloadAll={() => downloadAllFiles(genState.results)}
              />
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;
