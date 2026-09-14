import React from 'react';
import { Artifact, ArtifactFormat } from '../../types/artifact';
import { ArtifactHeader } from './ArtifactHeader';
import { SandboxIndicator } from './SandboxIndicator';
import { MarkdownRenderer } from './MarkdownRenderer';
import { HtmlSandboxFrame } from './HtmlSandboxFrame';

interface ArtifactViewerProps {
  artifact: Artifact | null;
  isOpen: boolean;
  format: ArtifactFormat;
  onFormatChange: (format: ArtifactFormat) => void;
  onClose: () => void;
  onTitleChange: (newTitle: string) => void;
  onToggleAllowScripts: (artifactId: string) => void;
  totalArtifactsCount: number;
  currentIndex: number;
  onNextArtifact: () => void;
  onPrevArtifact: () => void;
  onCopySuccess?: () => void;
  isMobileOverlay?: boolean;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({
  artifact,
  isOpen,
  format,
  onFormatChange,
  onClose,
  onTitleChange,
  onToggleAllowScripts,
  totalArtifactsCount,
  currentIndex,
  onNextArtifact,
  onPrevArtifact,
  onCopySuccess,
  isMobileOverlay = false,
}) => {
  if (!isOpen) return null;

  // Split lines for Source mode line numbering
  const sourceLines = artifact ? artifact.content.split('\n') : [];

  return (
    <aside
      aria-label="Artifact Workbench"
      className={`bg-paper-100 border-l border-line-200 flex flex-col h-full z-20 transition-all duration-base ease-out ${
        isMobileOverlay
          ? 'fixed inset-0 w-full z-50'
          : 'w-[440px] flex-shrink-0'
      }`}
    >
      {artifact ? (
        <>
          <ArtifactHeader
            artifact={artifact}
            format={format}
            onFormatChange={onFormatChange}
            onTitleChange={onTitleChange}
            onClose={onClose}
            totalArtifactsCount={totalArtifactsCount}
            currentIndex={currentIndex}
            onNextArtifact={onNextArtifact}
            onPrevArtifact={onPrevArtifact}
            onCopySuccess={onCopySuccess}
          />

          {/* Body */}
          <div className="flex-1 overflow-y-auto bg-paper-0 flex flex-col">
            {/* If HTML, show trust boundary strip at top */}
            {artifact.type === 'html' && format === 'rendered' && (
              <SandboxIndicator
                allowScripts={Boolean(artifact.allowScripts)}
                onToggleScripts={() => onToggleAllowScripts(artifact.id)}
              />
            )}

            <div className="p-6 flex-1">
              {format === 'source' ? (
                /* Source view with line numbers */
                <div className="font-mono text-xs text-ink-950 flex select-text">
                  <div className="pr-3 text-right text-ink-500 select-none border-r border-line-200 mr-3 font-mono">
                    {sourceLines.map((_, i) => (
                      <div key={i} className="leading-5">
                        {i + 1}
                      </div>
                    ))}
                  </div>
                  <pre className="flex-1 overflow-x-auto whitespace-pre font-mono leading-5">
                    {artifact.content}
                  </pre>
                </div>
              ) : artifact.type === 'html' ? (
                /* HTML sandboxed iframe */
                <HtmlSandboxFrame
                  htmlContent={artifact.content}
                  title={artifact.title}
                  allowScripts={Boolean(artifact.allowScripts)}
                />
              ) : (
                /* Rendered Markdown */
                <MarkdownRenderer content={artifact.content} />
              )}
            </div>
          </div>
        </>
      ) : (
        /* Empty state per Spec F.2 */
        <div className="flex-1 flex items-center justify-center p-6 bg-paper-0">
          <p className="font-serif text-sm text-ink-700 text-center">
            Generated essays and documents will appear here
          </p>
        </div>
      )}
    </aside>
  );
};
