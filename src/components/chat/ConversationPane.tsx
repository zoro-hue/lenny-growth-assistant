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
  onSwitchToCloud?: () => void;
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
  textareaRef,
}) => {
  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-paper-0">
      {messages.length === 0 ? (
        <div className="flex-1 overflow-y-auto">
          <EmptyState onSelectPrompt={onSendMessage} />
        </div>
      ) : (
        <MessageList
          messages={messages}
          artifacts={artifacts}
          loadingStage={loadingStage}
          onOpenArtifact={onOpenArtifact}
          onSwitchToCloud={onSwitchToCloud}
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
