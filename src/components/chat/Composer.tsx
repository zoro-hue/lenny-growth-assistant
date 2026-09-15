import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, FileText } from 'lucide-react';
import { ModelOption } from '../../types/chat';

interface ComposerProps {
  onSendMessage: (text: string, isEssay?: boolean) => void;
  isStreaming: boolean;
  activeModel: ModelOption;
  onOpenModelSelector?: () => void;
  textareaRef?: React.RefObject<HTMLTextAreaElement | null>;
}

export const Composer: React.FC<ComposerProps> = ({
  onSendMessage,
  isStreaming,
  activeModel,
  onOpenModelSelector,
  textareaRef: externalRef,
}) => {
  const [input, setInput] = useState('');
  const internalRef = useRef<HTMLTextAreaElement>(null);
  const ref = externalRef || internalRef;

  // Auto-resize textarea
  useEffect(() => {
    if (ref.current) {
      ref.current.style.height = 'auto';
      ref.current.style.height = `${Math.min(ref.current.scrollHeight, 180)}px`;
    }
  }, [input, ref]);

  const handleSend = (isEssay: boolean = false) => {
    if (!input.trim() || isStreaming) return;
    onSendMessage(input.trim(), isEssay);
    setInput('');
    if (ref.current) {
      ref.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(false);
    }
  };

  return (
    <div className="border-t border-line-200 bg-paper-0/95 backdrop-blur-sm px-4 sm:px-6 py-3.5 flex-shrink-0">
      <div className="max-w-[680px] mx-auto">
        <div className="bg-paper-0 border border-line-200 rounded-md shadow-sm focus-within:border-line-300 focus-within:ring-1 focus-within:ring-line-300 transition-all">
          {/* Top toolbar in composer: Model indicator chip + Essay action */}
          <div className="flex items-center justify-between px-3 pt-2.5 pb-1 border-b border-line-200/50">
            <button
              type="button"
              onClick={onOpenModelSelector}
              aria-label={`Active model: ${activeModel.name}. Click to change model.`}
              className="inline-flex items-center gap-1.5 text-xs font-sans text-ink-500 hover:text-ink-950 px-1.5 py-0.5 rounded hover:bg-paper-100 transition-colors duration-fast focus-visible:outline-evidence-600"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-evidence-600 flex-shrink-0" />
              <span>{activeModel.name}</span>
              <span className="text-ink-500 font-mono text-[10px]">
                ({activeModel.provider})
              </span>
            </button>

            <button
              type="button"
              onClick={() => handleSend(true)}
              disabled={!input.trim() || isStreaming}
              aria-label="Generate a Ship 30/30 playbook essay from prompt"
              className="inline-flex items-center gap-1 text-xs font-sans text-ink-700 hover:text-ink-950 disabled:opacity-40 disabled:hover:text-ink-700 px-2 py-0.5 rounded hover:bg-paper-100 transition-colors duration-fast focus-visible:outline-evidence-600"
            >
              <FileText className="w-3.5 h-3.5 text-evidence-600" />
              <span>Write an essay</span>
            </button>
          </div>

          {/* Text input area with click-to-focus on whole box */}
          <div
            onClick={() => ref.current?.focus()}
            className="flex items-end p-2 sm:p-2.5 gap-2 cursor-text"
          >
            <textarea
              ref={ref}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                isStreaming
                  ? "Generating response... (you can prepare your next query)"
                  : "Ask a question about Lenny's Podcast episodes... (press / to focus)"
              }
              rows={1}
              autoFocus
              className="flex-1 bg-transparent border-none outline-none resize-none font-sans text-[15px] leading-normal text-ink-950 placeholder:text-ink-500 px-1.5 py-1 min-h-[38px] max-h-[180px] cursor-text"
            />

            {isStreaming ? (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onSendMessage('', false); // Triggers abort
                }}
                title="Stop generation"
                aria-label="Stop generation"
                className="p-2 rounded-md bg-paper-200 text-ink-700 hover:bg-paper-300 hover:text-ink-950 transition-colors duration-fast flex-shrink-0 focus-visible:outline-evidence-600 shadow-xs"
              >
                <span className="w-3.5 h-3.5 block bg-ink-700 rounded-xs" />
              </button>
            ) : (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  handleSend(false);
                }}
                disabled={!input.trim()}
                aria-label="Send message"
                className="p-2 rounded-md bg-ink-950 text-paper-0 disabled:bg-paper-200 disabled:text-ink-400 hover:bg-ink-800 transition-colors duration-fast flex-shrink-0 focus-visible:outline-evidence-600 shadow-xs"
              >
                <ArrowUp className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between text-[11px] font-sans text-ink-500 mt-2 px-1">
          <span>
            Grounded in verbatim transcripts · Return to send, Shift+Return for newline
          </span>
          <span className="hidden sm:inline font-mono">⌘N new chat · / focus</span>
        </div>
      </div>
    </div>
  );
};
