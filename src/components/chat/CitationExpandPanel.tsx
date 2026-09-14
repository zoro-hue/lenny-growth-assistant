import React from 'react';
import { ExternalLink, Clock, Quote, X } from 'lucide-react';
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
  return (
    <div
      role="region"
      aria-label={`Citation details for ${citation.episodeTitle}`}
      className={`bg-paper-100 border border-line-200 rounded-md p-4 text-ink-950 text-sm font-sans transition-all duration-base ${
        isMobileDrawer ? 'shadow-xl' : 'mt-3 mb-2 animate-chip-in'
      }`}
    >
      <div className="flex items-start justify-between gap-3 mb-2.5">
        <div>
          <div className="flex items-center gap-2 text-xs text-ink-500 font-mono mb-1">
            <span>{citation.episodeNumber ? `EPISODE #${citation.episodeNumber}` : 'PODCAST ARCHIVE'}</span>
            <span>·</span>
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3 text-evidence-600" />
              {citation.timestamp}
            </span>
          </div>
          <h4 className="font-sans font-semibold text-ink-950 text-sm leading-snug">
            {citation.episodeTitle}
          </h4>
          {citation.guestRole && (
            <p className="text-xs text-ink-700 mt-0.5">
              <strong className="text-ink-950">{citation.guest}</strong> — {citation.guestRole}
            </p>
          )}
        </div>
        <button
          onClick={onClose}
          aria-label="Close citation details"
          className="text-ink-500 hover:text-ink-950 p-1 rounded hover:bg-paper-200 transition-colors duration-fast focus-visible:outline-evidence-600"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="relative pl-3.5 my-3 border-l-2 border-evidence-600">
        <Quote className="w-3 h-3 text-evidence-600 absolute -top-1 -left-1.5 opacity-50" />
        <p className="font-serif italic text-ink-700 text-sm leading-relaxed">
          &ldquo;{citation.quoteExcerpt}&rdquo;
        </p>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-line-200 mt-3 text-xs">
        <span className="text-ink-500">Verified against official audio transcript</span>
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
