import React from 'react';
import { ExternalLink, Clock, Quote, X, CheckCircle, ShieldCheck } from 'lucide-react';
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

  return (
    <div
      role="region"
      aria-label={`Source explorer for ${citation.guest} in ${citation.episodeTitle}`}
      className={`bg-paper-100 border border-line-300/80 rounded-md p-4 text-ink-950 text-sm font-sans transition-all duration-base shadow-sm ${
        isMobileDrawer ? 'shadow-xl' : 'mt-3 mb-2 animate-chip-in'
      }`}
    >
      {/* Top Header with SOURCE tag and Close */}
      <div className="flex items-start justify-between gap-3 mb-2.5">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono tracking-wider uppercase text-evidence-700 font-semibold mb-1">
            <span className="px-1.5 py-0.5 bg-evidence-100/90 rounded text-evidence-700">SOURCE</span>
            <span>·</span>
            <span>{citation.episodeNumber ? `EPISODE #${citation.episodeNumber}` : 'PODCAST ARCHIVE'}</span>
            <span>·</span>
            <span className="flex items-center gap-1 text-ink-600">
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

      {/* Verified Quote */}
      <div className="relative pl-3.5 my-3 border-l-2 border-evidence-600 bg-paper-0/60 p-2.5 rounded-r">
        <Quote className="w-3 h-3 text-evidence-600 absolute -top-1 -left-1.5 opacity-50" />
        <p className="font-serif italic text-ink-800 text-sm leading-relaxed">
          &ldquo;{citation.quoteExcerpt}&rdquo;
        </p>
      </div>

      {/* Why this source? */}
      <div className="my-2.5 pt-2 border-t border-line-200/70">
        <div className="text-[11px] font-sans font-semibold uppercase tracking-wider text-ink-500 mb-1">
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
          <span className="font-medium">Verified transcript source</span>
        </div>
        <a
          href={citation.episodeUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 font-medium text-evidence-600 hover:text-evidence-700 underline underline-offset-2 focus-visible:outline-evidence-600"
        >
          <span>Open episode</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </div>
  );
};
