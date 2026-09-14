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
  onSwitchToLocal?: () => void;
  onSelectSuggestion?: (suggestion: string) => void;
}

export const AssistantMessage: React.FC<AssistantMessageProps> = ({
  message,
  artifacts = {},
  onOpenArtifact,
  onSwitchToCloud,
  onSwitchToLocal,
  onSelectSuggestion,
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
                "Couldn't reach the model provider. Check connection settings or switch models."}
            </p>
            <div className="flex flex-wrap items-center gap-2">
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
              {message.errorDetails?.canSwitchToLocal && onSwitchToLocal && (
                <button
                  type="button"
                  onClick={onSwitchToLocal}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-paper-0 border border-line-300 rounded text-xs font-sans font-medium text-ink-950 hover:bg-paper-100 transition-colors duration-fast focus-visible:outline-evidence-600 shadow-sm"
                >
                  <span>Switch to Local Model (Ollama Llama 3.2 3B)</span>
                  <ArrowRight className="w-3.5 h-3.5 text-evidence-600" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Evidence confidence evaluation
  const citations = message.citations || [];
  const evidenceType: 'high' | 'limited' | 'not-grounded' =
    isLowEvidence || message.evidenceStrength === 'not-grounded'
      ? 'not-grounded'
      : message.evidenceStrength === 'limited' || citations.length === 1
      ? 'limited'
      : 'high';

  const defaultEvidenceLabel =
    evidenceType === 'not-grounded'
      ? 'No supporting Lenny Podcast evidence found'
      : citations.length >= 2
      ? `${citations.length} transcript sources · ${new Set(citations.map(c => c.guest)).size} speakers`
      : '1 relevant transcript source';

  const evidenceLabel = message.evidenceLabel || defaultEvidenceLabel;

  // Contextual follow-up suggestions
  const suggestions =
    message.followUpSuggestions && message.followUpSuggestions.length > 0
      ? message.followUpSuggestions
      : !isLowEvidence && !isError && !isStreaming
      ? [
          'Compare Brian Balfour and Elena Verna on growth loops',
          'What metric should I track?',
          'Turn this into a playbook',
          'Write a Ship 30/30 essay',
        ]
      : [];

  return (
    <div
      className={`my-6 max-w-[680px] transition-all duration-base ${
        isLowEvidence ? 'border-l-2 border-signal-amber-600 pl-4 py-1' : ''
      }`}
    >
      {/* Evidence confidence badge (NOT GROUNDED for low evidence, or HIGH/LIMITED above citations) */}
      {isLowEvidence && (
        <EvidenceConfidenceBadge
          type="not-grounded"
          label={evidenceLabel}
        />
      )}

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

      {/* Citations List with Evidence Strength Indicator */}
      {!isLowEvidence && citations.length > 0 && (
        <div className="mt-4 pt-3 border-t border-line-200">
          <div className="mb-2">
            <EvidenceConfidenceBadge
              type={evidenceType}
              label={evidenceLabel}
            />
          </div>
          <CitationList citations={citations} />
        </div>
      )}

      {/* Contextual Follow-up Suggestions ("Explore this further") */}
      {!isStreaming && !isError && suggestions.length > 0 && (
        <div className="mt-5 pt-3 border-t border-line-200/60">
          <div className="text-[11px] font-sans font-semibold text-ink-500 uppercase tracking-wider mb-2 select-none">
            Explore this further
          </div>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => onSelectSuggestion?.(suggestion)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-paper-100 hover:bg-paper-200/90 border border-line-200 text-xs font-sans text-ink-900 transition-colors duration-fast text-left shadow-xs focus-visible:outline-evidence-600"
              >
                <span className="text-evidence-600 font-bold text-xs">→</span>
                <span>{suggestion}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
