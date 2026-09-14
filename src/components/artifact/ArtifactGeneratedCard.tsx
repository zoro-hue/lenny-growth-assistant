import React from 'react';
import { FileText, ArrowUpRight } from 'lucide-react';
import { Artifact } from '../../types/artifact';

interface ArtifactGeneratedCardProps {
  artifact: Artifact;
  onOpen: (artifactId: string) => void;
}

export const ArtifactGeneratedCard: React.FC<ArtifactGeneratedCardProps> = ({
  artifact,
  onOpen,
}) => {
  return (
    <div
      onClick={() => onOpen(artifact.id)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onOpen(artifact.id);
        }
      }}
      tabIndex={0}
      role="button"
      aria-label={`Open generated document: ${artifact.title}`}
      className="mt-4 p-3.5 bg-paper-100 hover:bg-paper-200/70 border border-line-200 rounded-md cursor-pointer transition-colors duration-fast group focus-visible:outline-evidence-600"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-paper-0 border border-line-200 rounded text-evidence-600 flex-shrink-0 mt-0.5">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-mono uppercase tracking-wider text-ink-500">
                {artifact.type === 'html' ? 'Interactive Tool' : 'Ship 30/30 Playbook'}
              </span>
              <span className="text-line-300">·</span>
              <span className="text-xs text-ink-500 font-sans">
                {artifact.wordCount} words
              </span>
              <span className="text-line-300">·</span>
              <span className="text-xs text-ink-500 font-sans">
                {artifact.sourceCount} sources cited
              </span>
            </div>
            <h4 className="font-sans font-medium text-sm text-ink-950 group-hover:text-evidence-600 transition-colors duration-fast">
              {artifact.title}
            </h4>
          </div>
        </div>

        <div className="flex items-center gap-1 text-xs font-sans text-ink-500 group-hover:text-evidence-600 flex-shrink-0 mt-1">
          <span>Open Workbench</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </div>
      </div>
    </div>
  );
};
