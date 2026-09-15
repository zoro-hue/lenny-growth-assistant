import React, { useEffect, useRef } from 'react';
import { Message } from '../../types/chat';
import { Artifact } from '../../types/artifact';
import { UserMessage } from './UserMessage';
import { AssistantMessage } from './AssistantMessage';
import { LoadingIndicator } from './LoadingIndicator';

interface MessageListProps {
  messages: Message[];
  artifacts?: Record<string, Artifact>;
  loadingStage: string | null;
  activeModelId?: string;
  onOpenArtifact?: (artifactId: string) => void;
  onSwitchToCloud?: (errorMsgId?: string) => void;
  onSwitchToLocal?: (errorMsgId?: string) => void;
  onRetry?: (errorMsgId?: string) => void;
  onSelectSuggestion?: (suggestion: string) => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  artifacts,
  loadingStage,
  activeModelId,
  onOpenArtifact,
  onSwitchToCloud,
  onSwitchToLocal,
  onRetry,
  onSelectSuggestion,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loadingStage]);

  return (
    <div
      role="log"
      aria-live="polite"
      aria-relevant="additions text"
      className="flex-1 overflow-y-auto px-4 sm:px-6 py-6"
    >
      <div className="max-w-[680px] mx-auto">
        {messages.map(msg => {
          if (msg.role === 'system') {
            return (
              <div
                key={msg.id}
                className="my-4 text-center text-xs font-sans text-ink-500 select-none"
              >
                <span>{msg.content}</span>
              </div>
            );
          }
          if (msg.role === 'user') {
            return <UserMessage key={msg.id} message={msg} />;
          }
          return (
            <AssistantMessage
              key={msg.id}
              message={msg}
              artifacts={artifacts}
              activeModelId={activeModelId}
              onOpenArtifact={onOpenArtifact}
              onSwitchToCloud={onSwitchToCloud}
              onSwitchToLocal={onSwitchToLocal}
              onRetry={onRetry}
              onSelectSuggestion={onSelectSuggestion}
            />
          );
        })}

        {loadingStage && <LoadingIndicator statusText={loadingStage} />}

        <div ref={bottomRef} />
      </div>
    </div>
  );
};
