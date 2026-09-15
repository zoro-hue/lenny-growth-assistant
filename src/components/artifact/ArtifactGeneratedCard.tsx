import React from 'react';
import { FileText, Code, Feather, ClipboardList, BookOpen, ArrowUpRight } from 'lucide-react';
import { Artifact } from '../../types/artifact';

interface ArtifactGeneratedCardProps {
  artifact: Artifact;
  onOpen: (artifactId: string) => void;
}

export const ArtifactGeneratedCard: React.FC<ArtifactGeneratedCardProps> = ({
  artifact,
  onOpen,
}) => {
  // Determine distinct icon based on Section 15
  const getIconAndLabel = () => {
    const titleLower = artifact.title.toLowerCase();
    if (artifact.type === 'html') {
      return { icon: Code, label: 'HTML Artifact' };
    }
    if (titleLower.includes('ship 30') || titleLower.includes('essay')) {
      return { icon: Feather, label: 'Ship 30/30 Essay' };
    }
    if (titleLower.includes('prd') || titleLower.includes('spec')) {
      return { icon: ClipboardList, label: 'Product Spec' };
    }
    if (titleLower.includes('playbook')) {
      return { icon: BookOpen, label: 'Strategy Playbook' };
    }
    return { icon: FileText, label: 'Markdown Document' };
  };

  const { icon: ArtifactIcon, label: typeLabel } = getIconAndLabel();

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
      className="mt-4 p-3.5 bg-paper-100/90 hover:bg-paper-200/80 border border-line-200 hover:border-line-300 rounded-md cursor-pointer transition-all duration-150 hover:-translate-y-0.5 shadow-xs group focus-visible:outline-evidence-600"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <div className="p-2 bg-paper-0 border border-line-200 rounded text-evidence-600 flex-shrink-0 mt-0.5 group-hover:border-evidence-600/30 group-hover:scale-105 transition-all duration-150">
            <ArtifactIcon className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            {/* Secondary artifact category label & smaller metadata */}
            <div className="flex items-center gap-2 mb-1 text-[11px]">
              <span className="text-[10px] font-mono uppercase tracking-wider text-ink-500 font-medium">
                {typeLabel}
              </span>
              <span className="text-line-300">·</span>
              <span className="text-[11px] text-ink-500 font-sans">
                {artifact.wordCount} words
              </span>
              {artifact.sourceCount !== undefined && artifact.sourceCount > 0 && (
                <>
                  <span className="text-line-300">·</span>
                  <span className="text-[11px] text-ink-500 font-sans">
                    {artifact.sourceCount} sources cited
                  </span>
                </>
              )}
            </div>
            {/* Prominent editorial document title */}
            <h4 className="font-serif font-semibold text-[15px] sm:text-base text-ink-950 leading-snug tracking-tight group-hover:text-evidence-800 transition-colors duration-150 truncate">
              {artifact.title}
            </h4>
          </div>
        </div>

        {/* Clearly clickable Workbench action */}
        <div className="inline-flex items-center gap-1 px-2 py-1 rounded bg-paper-0/90 group-hover:bg-paper-0 border border-line-200 group-hover:border-evidence-600/30 text-ink-700 group-hover:text-evidence-700 text-xs font-sans transition-all duration-150 flex-shrink-0 shadow-2xs mt-0.5">
          <span className="text-[11px] font-mono font-medium">Workbench</span>
          <ArrowUpRight className="w-3.5 h-3.5 text-evidence-600 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-150" />
        </div>
      </div>
    </div>
  );
};
