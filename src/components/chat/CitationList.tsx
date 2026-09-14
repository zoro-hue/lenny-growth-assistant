import React, { useState } from 'react';
import { Citation } from '../../types/chat';
import { CitationChip } from './CitationChip';
import { CitationExpandPanel } from './CitationExpandPanel';

interface CitationListProps {
  citations: Citation[];
}

export const CitationList: React.FC<CitationListProps> = ({ citations }) => {
  const [activeCitationId, setActiveCitationId] = useState<string | null>(null);

  if (!citations || citations.length === 0) return null;

  const activeCitation = citations.find(c => c.id === activeCitationId) || null;

  const handleToggle = (citationId: string) => {
    setActiveCitationId(prev => (prev === citationId ? null : citationId));
  };

  return (
    <div className="mt-4 pt-3 border-t border-line-200">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs font-sans font-medium text-ink-700 tracking-normal">
          Transcript Grounding ({citations.length}):
        </span>
      </div>

      {/* Row of chips */}
      <div className="flex flex-wrap items-center gap-2">
        {citations.map((cit, idx) => (
          <CitationChip
            key={cit.id}
            citation={cit}
            index={idx}
            isSelected={activeCitationId === cit.id}
            onClick={() => handleToggle(cit.id)}
          />
        ))}
      </div>

      {/* Inline expandable details panel */}
      {activeCitation && (
        <div className="mt-3">
          <CitationExpandPanel
            citation={activeCitation}
            onClose={() => setActiveCitationId(null)}
          />
        </div>
      )}
    </div>
  );
};
