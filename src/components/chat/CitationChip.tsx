import React from 'react';
import { FileText } from 'lucide-react';
import { Citation } from '../../types/chat';

interface CitationChipProps {
  citation: Citation;
  index: number;
  isSelected: boolean;
  onClick: () => void;
}

export const CitationChip: React.FC<CitationChipProps> = ({
  citation,
  index,
  isSelected,
  onClick,
}) => {
  const shortTitle = citation.episodeNumber
    ? `Ep ${citation.episodeNumber} · ${citation.guest}`
    : `${citation.guest}`;

  return (
    <button
      type="button"
      onClick={onClick}
      aria-expanded={isSelected}
      aria-label={`View transcript source: ${citation.guest} in ${citation.episodeTitle}`}
      style={{ animationDelay: `${index * 40}ms` }}
      className={`group inline-flex items-center gap-1.5 px-2.5 py-1 rounded-pill text-xs font-sans font-medium transition-all duration-150 select-none animate-chip-in focus-visible:outline-evidence-600 ${
        isSelected
          ? 'bg-evidence-600 text-paper-0 shadow-xs ring-1 ring-evidence-700 -translate-y-0.5'
          : 'bg-evidence-100 text-evidence-700 hover:bg-[#d9e5df] hover:-translate-y-0.5 hover:shadow-xs'
      }`}
    >
      <FileText className="w-3 h-3 flex-shrink-0 transition-transform duration-150 group-hover:scale-110" />
      <span className="truncate max-w-[200px]">{shortTitle}</span>
      <span className="text-[11px] opacity-75 font-mono">@{citation.timestamp}</span>
    </button>
  );
};

