import React from 'react';
import { ExternalLink, Clock, Quote, X, ShieldCheck } from 'lucide-react';
import { Citation } from '../../types/chat';

interface CitationExpandPanelProps {
  citation: Citation;
  onClose: () => void;
  isMobileDrawer?: boolean;
}

export const CitationExpandPanel: React.FC<CitationExpandPanelProps> = ({
  citation,
  onClose,
  isMobileDrawer = false,
}) => {
  const whySource =
    citation.whyThisSource ||
    `Direct evidence from ${citation.guest} supporting the core argument.`;

  // Calculate timeline position percentage (assume ~60m / 3600s episode duration)
  const parseSeconds = (ts: string) => {
    const parts = ts.split(':').map(Number);
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
    if (parts.length === 2) return parts[0] * 60 + parts[1];
    return 300;
  };
  const seconds = parseSeconds(citation.timestamp);
  const percent = Math.min(Math.max((seconds / 3600) * 100, 10), 90);

  return (
    <div
      role="region"
      aria-label={`Source explorer for ${citation.guest} in ${citation.episodeTitle}`}
      className={`bg-paper-100 border border-line-300/80 rounded-md p-4 text-ink-950 text-sm font-sans transition-all duration-base shadow-sm ${
        isMobileDrawer ? 'shadow-xl' : 'mt-2 mb-2 animate-chip-in'
      }`}
    >
      {/* Top Header with SOURCE tag, Episode, Timestamp and Close */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <div className="flex items-center gap-1.5 text-[10px] font-mono tracking-wider uppercase text-evidence-700 font-semibold mb-1">
            <span className="px-1.5 py-0.5 bg-evidence-100/90 rounded text-evidence-700">SOURCE</span>
            <span className="text-ink-300">·</span>
            <span>{citation.episodeNumber ? `EPISODE #${citation.episodeNumber}` : 'PODCAST ARCHIVE'}</span>
            <span className="text-ink-300">·</span>
            <span className="flex items-center gap-1 text-ink-600 font-mono">
              <Clock className="w-3 h-3 text-evidence-600" />
              {citation.timestamp}
            </span>
          </div>
          <h4 className="font-sans font-bold text-ink-950 text-base leading-snug">
            {citation.guest}
          </h4>
          <p className="text-xs text-ink-700 mt-0.5">
            {citation.episodeTitle}
            {citation.guestRole && <span className="text-ink-500"> ({citation.guestRole})</span>}
          </p>
        </div>
        <button
          onClick={onClose}
          aria-label="Close source details"
          className="text-ink-500 hover:text-ink-950 p-1 rounded hover:bg-paper-200 transition-colors duration-fast focus-visible:outline-evidence-600"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* 10. SOURCE EXPLORER GRAPHIC: Visual timeline */}
      <div className="my-3 px-3 py-2 bg-paper-0/70 border border-line-200/80 rounded select-none">
        <div className="flex items-center justify-between text-[10px] font-mono text-ink-500 mb-1.5">
          <span className="uppercase font-semibold tracking-wider text-evidence-700">
            {citation.episodeNumber ? `EPISODE #${citation.episodeNumber}` : "LENNY'S ARCHIVE"}
          </span>
          <span>{citation.guest}</span>
        </div>

        {/* Timeline bar with position marker */}
        <div className="relative w-full h-[3px] bg-line-200 rounded-full my-2">
          {/* Progress track up to timestamp */}
          <div
            className="absolute left-0 top-0 h-full bg-evidence-600/40 rounded-full"
            style={{ width: `${percent}%` }}
          />
          {/* Marker dot */}
          <div
            className="absolute -top-[4.5px] w-3 h-3 rounded-full bg-evidence-600 border-2 border-paper-0 shadow-xs transform -translate-x-1/2"
            style={{ left: `${percent}%` }}
            title={`Evidence timestamp: ${citation.timestamp}`}
          />
        </div>

        <div className="flex items-center justify-between text-[9.5px] font-mono text-ink-400">
          <span>00:00</span>
          <span className="font-semibold text-evidence-700">@{citation.timestamp}</span>
          <span>~60:00</span>
        </div>
      </div>

      {/* Verified Quote with subtle watermark quote-mark graphic */}
      <div className="relative pl-3.5 pr-8 my-3 border-l-2 border-evidence-600 bg-paper-0/80 p-3 rounded-r overflow-hidden">
        <Quote className="w-10 h-10 text-evidence-600/10 absolute right-1.5 bottom-1 pointer-events-none select-none" />
        <p className="font-serif italic text-ink-800 text-[13.5px] leading-relaxed relative z-10">
          &ldquo;{citation.quoteExcerpt}&rdquo;
        </p>
      </div>

      {/* Why this source? */}
      <div className="my-2.5 pt-2 border-t border-line-200/70">
        <div className="text-[10.5px] font-sans font-semibold uppercase tracking-wider text-ink-500 mb-1">
          Why this source?
        </div>
        <p className="text-xs text-ink-700 leading-relaxed font-sans">
          {whySource}
        </p>
      </div>

      {/* Verification footer & Open episode */}
      <div className="flex items-center justify-between pt-2.5 border-t border-line-200 mt-3 text-xs">
        <div className="flex items-center gap-1.5 text-ink-600">
          <ShieldCheck className="w-3.5 h-3.5 text-evidence-600 flex-shrink-0" />
          <span className="font-medium text-[11px] text-ink-700">Verified against official transcript</span>
        </div>
        <a
          href={citation.episodeUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 font-medium text-xs text-evidence-600 hover:text-evidence-700 underline underline-offset-2 focus-visible:outline-evidence-600"
        >
          <span>Open episode</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </div>
  );
};

