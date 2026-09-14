import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { AlertTriangle, ArrowRight } from 'lucide-react';
import { Message } from '../../types/chat';
import { Artifact } from '../../types/artifact';
import { CitationList } from './CitationList';
import { EvidenceConfidenceBadge } from './EvidenceConfidenceBadge';
import { ArtifactGeneratedCard } from '../artifact/ArtifactGeneratedCard';

interface AssistantMessageProps {
  message: Message;
  artifacts?: Record<string, Artifact>;
  onOpenArtifact?: (artifactId: string) => void;
  onSwitchToCloud?: () => void;
}

export const AssistantMessage: React.FC<AssistantMessageProps> = ({
  message,
  artifacts = {},
  onOpenArtifact,
  onSwitchToCloud,
}) => {
  const isStreaming = message.status === 'streaming';
  const isLowEvidence = message.status === 'low-evidence';
  const isError = message.status === 'error';
  const artifact = message.artifactId ? artifacts[message.artifactId] : undefined;

  if (isError) {
    return (
      <div className="my-6 max-w-[680px]">
        <div className="bg-error-100 text-error-700 p-4 rounded-sm border border-error-700/20 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5 text-error-700" />
          <div className="flex-1">
            <h4 className="font-sans font-semibold text-sm mb-1 text-error-700">
              Model Connection Failed
            </h4>
            <p className="font-sans text-sm text-ink-950 mb-3">
              {message.errorDetails?.message ||
                "Couldn't reach the local model. Check that Ollama is running on localhost:11434, or switch to Cloud."}
            </p>
            {message.errorDetails?.canSwitchToCloud && onSwitchToCloud && (
              <button
                type="button"
                onClick={onSwitchToCloud}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-paper-0 border border-line-300 rounded text-xs font-sans font-medium text-ink-950 hover:bg-paper-100 transition-colors duration-fast focus-visible:outline-evidence-600 shadow-sm"
              >
                <span>Switch to Cloud (OpenAI GPT-4o mini)</span>
                <ArrowRight className="w-3.5 h-3.5 text-evidence-600" />
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`my-6 max-w-[680px] transition-all duration-base ${
        isLowEvidence ? 'border-l-2 border-signal-amber-600 pl-4 py-1' : ''
      }`}
    >
      {/* Evidence confidence badge for low-evidence state */}
      {isLowEvidence && <EvidenceConfidenceBadge />}

      {/* Message body in Source Serif 4 */}
      <div className="font-serif text-[17px] leading-[1.75] text-ink-950">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => (
              <h2 className="font-sans font-semibold text-lg text-ink-950 mt-5 mb-2">
                {children}
              </h2>
            ),
            h2: ({ children }) => (
              <h3 className="font-sans font-semibold text-base text-ink-950 mt-4 mb-2">
                {children}
              </h3>
            ),
            h3: ({ children }) => (
              <h4 className="font-sans font-semibold text-sm text-ink-950 mt-3 mb-1.5">
                {children}
              </h4>
            ),
            p: ({ children }) => <p className="mb-3.5 last:mb-0">{children}</p>,
            ul: ({ children }) => (
              <ul className="list-disc pl-5 mb-3.5 space-y-1">{children}</ul>
            ),
            ol: ({ children }) => (
              <ol className="list-decimal pl-5 mb-3.5 space-y-1">{children}</ol>
            ),
            li: ({ children }) => <li>{children}</li>,
            blockquote: ({ children }) => (
              <blockquote className="border-l-2 border-evidence-600 pl-4 my-3 italic text-ink-700">
                {children}
              </blockquote>
            ),
            code: ({ children, className }) => {
              const isBlock = className && className.includes('language-');
              if (isBlock) {
                return (
                  <code className="block font-mono text-xs bg-paper-100 p-3 rounded-md border border-line-200 overflow-x-auto text-ink-950 my-2">
                    {children}
                  </code>
                );
              }
              return (
                <code className="font-mono text-xs bg-paper-100 px-1.5 py-0.5 rounded text-ink-950 border border-line-200">
                  {children}
                </code>
              );
            },
          }}
        >
          {message.content}
        </ReactMarkdown>

        {/* Streaming caret */}
        {isStreaming && (
          <span
            className="inline-block w-1.5 h-4 ml-0.5 bg-evidence-600 animate-pulse-dot align-middle"
            aria-hidden="true"
          />
        )}
      </div>

      {/* Inline Artifact Generated Card */}
      {artifact && onOpenArtifact && (
        <ArtifactGeneratedCard artifact={artifact} onOpen={onOpenArtifact} />
      )}

      {/* Citations List (Structural proof-of-grounding, only when complete and citations exist) */}
      {!isLowEvidence && message.citations && message.citations.length > 0 && (
        <CitationList citations={message.citations} />
      )}
    </div>
  );
};
