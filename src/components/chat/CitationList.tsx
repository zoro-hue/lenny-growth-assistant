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
  const uniqueSpeakers = Array.from(new Set(citations.map(c => c.guest)));

  const handleToggle = (citationId: string) => {
    setActiveCitationId(prev => (prev === citationId ? null : citationId));
  };

  return (
    <div className="mt-4 pt-3 border-t border-line-200">
      {/* Evidence Header */}
      <div className="flex items-center justify-between gap-2 mb-2.5 select-none">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono font-bold tracking-wider uppercase text-evidence-700 bg-evidence-100/90 px-1.5 py-0.5 rounded">
            EVIDENCE
          </span>
          <span className="text-xs font-sans font-medium text-ink-700">
            ● {citations.length} transcript {citations.length === 1 ? 'source' : 'sources'} · {uniqueSpeakers.length} {uniqueSpeakers.length === 1 ? 'speaker' : 'speakers'}
          </span>
        </div>
        <span className="text-[11px] font-sans text-ink-500">
          Click source to inspect
        </span>
      </div>

      {/* Tiny vertical evidence timeline (visual indicator: answer -> evidence -> sources) */}
      <div className="mb-3 pl-1 flex flex-col gap-1 border-l border-evidence-600/30 ml-2 py-0.5">
        {citations.map((c, i) => (
          <div
            key={`timeline-${c.id}-${i}`}
            className="flex items-center gap-2 text-[11px] font-sans text-ink-600 -ml-[5px]"
          >
            <span
              className={`w-2 h-2 rounded-full flex-shrink-0 transition-colors ${
                activeCitationId === c.id
                  ? 'bg-evidence-600 ring-2 ring-evidence-100'
                  : 'bg-evidence-600/70'
              }`}
            />
            <span className="font-medium text-ink-900">{c.guest}</span>
            <span className="text-ink-500 font-mono text-[10px]">
              {c.episodeNumber ? `Ep ${c.episodeNumber}` : ''} @ {c.timestamp}
            </span>
          </div>
        ))}
      </div>

      {/* Row of interactive citation chips */}
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

      {/* Inline expandable details panel with Source Explorer Graphic */}
      {activeCitation && (
        <div className="mt-3 animate-chip-in">
          <CitationExpandPanel
            citation={activeCitation}
            onClose={() => setActiveCitationId(null)}
          />
        </div>
      )}
    </div>
  );
};

