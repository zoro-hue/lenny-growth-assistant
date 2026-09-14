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
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-pill text-xs font-sans font-medium transition-all duration-fast select-none animate-chip-in focus-visible:outline-evidence-600 ${
        isSelected
          ? 'bg-evidence-600 text-paper-0 shadow-sm'
          : 'bg-evidence-100 text-evidence-600 hover:bg-[#dbe7e1]'
      }`}
    >
      <FileText className="w-3 h-3 flex-shrink-0" />
      <span className="truncate max-w-[200px]">{shortTitle}</span>
      <span className="text-[11px] opacity-75 font-mono">@{citation.timestamp}</span>
    </button>
  );
};
