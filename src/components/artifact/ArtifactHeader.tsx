import React, { useState } from 'react';
import { Copy, Download, X, ChevronLeft, ChevronRight, Check } from 'lucide-react';
import { Artifact, ArtifactFormat } from '../../types/artifact';

interface ArtifactHeaderProps {
  artifact: Artifact;
  format: ArtifactFormat;
  onFormatChange: (format: ArtifactFormat) => void;
  onTitleChange: (newTitle: string) => void;
  onClose: () => void;
  totalArtifactsCount: number;
  currentIndex: number;
  onNextArtifact: () => void;
  onPrevArtifact: () => void;
  onCopySuccess?: () => void;
}

export const ArtifactHeader: React.FC<ArtifactHeaderProps> = ({
  artifact,
  format,
  onFormatChange,
  onTitleChange,
  onClose,
  totalArtifactsCount,
  currentIndex,
  onNextArtifact,
  onPrevArtifact,
  onCopySuccess,
}) => {
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [titleInput, setTitleInput] = useState(artifact.title);
  const [copied, setCopied] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  const handleTitleSubmit = () => {
    setIsEditingTitle(false);
    if (titleInput.trim()) {
      onTitleChange(titleInput.trim());
    } else {
      setTitleInput(artifact.title);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(artifact.content);
      setCopied(true);
      onCopySuccess?.();
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // fallback
    }
  };

  const handleDownload = () => {
    const blob = new Blob([artifact.content], {
      type: artifact.type === 'html' ? 'text/html;charset=utf-8' : 'text/markdown;charset=utf-8',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const extension = artifact.type === 'html' ? 'html' : 'md';
    const safeTitle = artifact.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 32);
    a.download = `${safeTitle || 'artifact'}.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setDownloaded(true);
    setTimeout(() => setDownloaded(false), 1500);
  };

  return (
    <div className="h-[44px] bg-paper-100 border-b border-line-200 px-3 flex items-center justify-between gap-2 flex-shrink-0 select-none">
      {/* Title & Stepper */}
      <div className="flex items-center gap-2 min-w-0 flex-1">
        {totalArtifactsCount > 1 && (
          <div className="flex items-center gap-0.5 text-xs text-ink-500 font-mono flex-shrink-0">
            <button
              type="button"
              disabled={currentIndex <= 0}
              onClick={onPrevArtifact}
              aria-label="Previous artifact version"
              className="p-1 rounded hover:bg-paper-200 disabled:opacity-30 disabled:hover:bg-transparent"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span className="px-0.5">
              {currentIndex + 1}/{totalArtifactsCount}
            </span>
            <button
              type="button"
              disabled={currentIndex >= totalArtifactsCount - 1}
              onClick={onNextArtifact}
              aria-label="Next artifact version"
              className="p-1 rounded hover:bg-paper-200 disabled:opacity-30 disabled:hover:bg-transparent"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {isEditingTitle ? (
          <input
            type="text"
            value={titleInput}
            onChange={(e) => setTitleInput(e.target.value)}
            onBlur={handleTitleSubmit}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleTitleSubmit();
              if (e.key === 'Escape') {
                setTitleInput(artifact.title);
                setIsEditingTitle(false);
              }
            }}
            autoFocus
            className="font-sans font-medium text-xs sm:text-sm text-ink-950 bg-paper-0 border border-line-300 rounded px-1.5 py-0.5 w-full outline-none focus:border-evidence-600"
          />
        ) : (
          <button
            type="button"
            onClick={() => {
              setTitleInput(artifact.title);
              setIsEditingTitle(true);
            }}
            title="Click to rename document"
            className="truncate text-left font-sans font-medium text-xs sm:text-sm text-ink-950 hover:text-evidence-600 truncate py-0.5 rounded focus-visible:outline-evidence-600"
          >
            {artifact.title}
          </button>
        )}
      </div>

      {/* Format Toggle & Actions */}
      <div className="flex items-center gap-1.5 flex-shrink-0">
        {/* Rendered / Source toggle */}
        <div className="flex items-center bg-paper-200/80 p-0.5 rounded text-xs font-sans">
          <button
            type="button"
            onClick={() => onFormatChange('rendered')}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-all ${
              format === 'rendered'
                ? 'bg-paper-0 text-ink-950 shadow-xs'
                : 'text-ink-700 hover:text-ink-950'
            }`}
          >
            Rendered
          </button>
          <button
            type="button"
            onClick={() => onFormatChange('source')}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-all ${
              format === 'source'
                ? 'bg-paper-0 text-ink-950 shadow-xs'
                : 'text-ink-700 hover:text-ink-950'
            }`}
          >
            Source
          </button>
        </div>

        {/* Copy button */}
        <button
          type="button"
          onClick={handleCopy}
          aria-label="Copy raw document source"
          title="Copy raw markdown/html"
          className="inline-flex items-center gap-1 px-2 py-1 rounded text-ink-700 hover:text-ink-950 hover:bg-paper-200 transition-colors duration-fast focus-visible:outline-evidence-600"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-evidence-600" />
              <span className="text-[11px] font-mono text-evidence-700 font-medium">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span className="text-[11px] font-mono">Copy</span>
            </>
          )}
        </button>

        {/* Download button */}
        <button
          type="button"
          onClick={handleDownload}
          aria-label={`Download document as ${artifact.type === 'html' ? '.html' : '.md'}`}
          title="Download document file"
          className="p-1.5 rounded text-ink-700 hover:text-ink-950 hover:bg-paper-200 transition-colors duration-fast focus-visible:outline-evidence-600"
        >
          {downloaded ? (
            <Check className="w-3.5 h-3.5 text-evidence-600" />
          ) : (
            <Download className="w-3.5 h-3.5" />
          )}
        </button>

        {/* Close (x) */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close Artifact Workbench"
          title="Close workbench (Esc)"
          className="p-1.5 rounded text-ink-700 hover:text-ink-950 hover:bg-paper-200 transition-colors duration-fast focus-visible:outline-evidence-600"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
