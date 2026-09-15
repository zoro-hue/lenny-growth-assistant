import React from 'react';
import { Message, ModelOption } from '../../types/chat';
import { Artifact } from '../../types/artifact';
import { MessageList } from './MessageList';
import { EmptyState } from './EmptyState';
import { Composer } from './Composer';

interface ConversationPaneProps {
  messages: Message[];
  artifacts?: Record<string, Artifact>;
  isStreaming: boolean;
  loadingStage: string | null;
  activeModel: ModelOption;
  onSendMessage: (text: string, isEssay?: boolean) => void;
  onOpenArtifact?: (artifactId: string) => void;
  onOpenModelSelector?: () => void;
  onSwitchToCloud?: (errorMsgId?: string) => void;
  onSwitchToLocal?: (errorMsgId?: string) => void;
  onRetry?: (errorMsgId?: string) => void;
  textareaRef?: React.RefObject<HTMLTextAreaElement | null>;
}

export const ConversationPane: React.FC<ConversationPaneProps> = ({
  messages,
  artifacts,
  isStreaming,
  loadingStage,
  activeModel,
  onSendMessage,
  onOpenArtifact,
  onOpenModelSelector,
  onSwitchToCloud,
  onSwitchToLocal,
  onRetry,
  textareaRef,
}) => {
  const hasChatContent = messages.some(
    m => m.role === 'user' || m.role === 'assistant'
  );

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-paper-0">
      {!hasChatContent ? (
        <div className="flex-1 overflow-y-auto">
          {messages.map(
            msg =>
              msg.role === 'system' && (
                <div
                  key={msg.id}
                  className="mt-4 text-center text-xs font-sans text-ink-500 select-none"
                >
                  <span>{msg.content}</span>
                </div>
              )
          )}
          <EmptyState onSelectPrompt={onSendMessage} />
        </div>
      ) : (
        <MessageList
          messages={messages}
          artifacts={artifacts}
          loadingStage={loadingStage}
          activeModelId={activeModel.id}
          onOpenArtifact={onOpenArtifact}
          onSwitchToCloud={onSwitchToCloud}
          onSwitchToLocal={onSwitchToLocal}
          onRetry={onRetry}
          onSelectSuggestion={(suggestion) => {
            const lower = suggestion.toLowerCase();
            const isEssay = lower.includes('essay') || lower.includes('ship 30');
            onSendMessage(suggestion, isEssay);
          }}
        />
      )}

      <Composer
        onSendMessage={onSendMessage}
        isStreaming={isStreaming}
        activeModel={activeModel}
        onOpenModelSelector={onOpenModelSelector}
        textareaRef={textareaRef}
      />
    </div>
  );
};
