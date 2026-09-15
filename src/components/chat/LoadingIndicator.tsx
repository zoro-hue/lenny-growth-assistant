import React from 'react';
import { Search } from 'lucide-react';

interface LoadingIndicatorProps {
  statusText?: string;
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  statusText = 'Searching transcripts...',
}) => {
  return (
    <div
      role="status"
      aria-live="polite"
      className="my-6 max-w-[680px] p-4 bg-paper-100/70 border border-line-200 rounded-md select-none animate-message-in"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Search className="w-3.5 h-3.5 text-evidence-600 animate-pulse-dot" />
          <span className="font-mono text-[11px] uppercase tracking-wider font-semibold text-evidence-700">
            Researching Transcript Evidence
          </span>
        </div>
        <span className="font-mono text-[10px] text-ink-500">
          Grounded Analysis
        </span>
      </div>

      {/* Subtle scanning indicator line */}
      <div className="relative w-full h-[2px] bg-line-200 rounded-full my-3 overflow-hidden">
        <div
          className="animate-scanner-dot w-2.5 h-2.5 rounded-full bg-evidence-600 -top-[4px] shadow-xs"
          aria-hidden="true"
        />
      </div>

      {/* Calm status message */}
      <div className="flex items-center justify-between text-xs font-sans text-ink-700 pt-0.5">
        <span className="truncate">{statusText}</span>
        <span className="text-[11px] font-mono text-ink-400">Podcast Archive</span>
      </div>
    </div>
  );
};

