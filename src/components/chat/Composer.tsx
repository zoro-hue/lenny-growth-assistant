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
    <div className="border-t border-line-200 bg-paper-0/95 backdrop-blur-sm px-4 sm:px-6 py-3 flex-shrink-0">
      <div className="max-w-[680px] mx-auto">
        <div className="bg-paper-0 border border-line-200 rounded-md shadow-xs focus-within:border-line-300 focus-within:ring-1 focus-within:ring-line-300 transition-all">
          {/* Top toolbar in composer: Aligned provider chip + secondary essay trigger */}
          <div className="flex items-center justify-between px-3 pt-2 pb-1 border-b border-line-200/50">
            <button
              type="button"
              onClick={onOpenModelSelector}
              aria-label={`Active model: ${activeModel.name}. Click to change model.`}
              className="inline-flex items-center gap-1.5 text-xs font-sans text-ink-600 hover:text-ink-950 px-1.5 py-0.5 rounded hover:bg-paper-100 transition-colors duration-fast focus-visible:outline-evidence-600"
            >
              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${isStreaming ? 'bg-evidence-600 animate-ping' : 'bg-evidence-600'}`} />
              <span className="font-medium text-ink-800">{activeModel.name}</span>
              <span className="text-ink-400 font-mono text-[10.5px]">
                · {activeModel.provider}
              </span>
            </button>

            {/* Subtle secondary action: doesn't compete with primary composer input */}
            <button
              type="button"
              onClick={() => handleSend(true)}
              disabled={!input.trim() || isStreaming}
              aria-label="Generate a Ship 30/30 playbook essay from prompt"
              className="inline-flex items-center gap-1 text-[11px] font-sans text-ink-500 hover:text-ink-800 disabled:opacity-35 disabled:hover:text-ink-500 px-2 py-0.5 rounded hover:bg-paper-100 transition-colors duration-fast focus-visible:outline-evidence-600"
            >
              <FileText className="w-3 h-3 text-evidence-600/80" />
              <span>Write an essay</span>
            </button>
          </div>

          {/* Text input area with comfortable padding & vertically centered send button */}
          <div
            onClick={() => ref.current?.focus()}
            className="flex items-center p-2 sm:p-2.5 gap-2 cursor-text min-h-[46px]"
          >
            <textarea
              ref={ref}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                isStreaming
                  ? "Synthesizing research from podcast transcripts… (you can draft your next prompt)"
                  : "Ask a question about Lenny's Podcast episodes… (press / to focus)"
              }
              rows={1}
              autoFocus
              className="flex-1 bg-transparent border-none outline-none resize-none font-sans text-[14.5px] sm:text-[15px] leading-relaxed text-ink-950 placeholder:text-ink-400 px-2.5 py-1 min-h-[36px] max-h-[180px] cursor-text"
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
                className="p-2 rounded-md bg-paper-200 text-ink-700 hover:bg-paper-300 hover:text-ink-950 transition-colors duration-fast flex-shrink-0 focus-visible:outline-evidence-600 shadow-2xs self-center"
              >
                <span className="w-3.5 h-3.5 block bg-ink-700 rounded-xs animate-pulse" />
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
                className="p-2 rounded-md bg-ink-950 text-paper-0 disabled:bg-paper-200/80 disabled:text-ink-400/60 disabled:cursor-not-allowed disabled:shadow-none hover:bg-ink-800 transition-colors duration-fast flex-shrink-0 focus-visible:outline-evidence-600 shadow-xs self-center"
              >
                <ArrowUp className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Subtle, restrained keyboard shortcut & attribution line */}
        <div className="flex items-center justify-between text-[10.5px] font-sans text-ink-400 mt-1.5 px-1 select-none">
          <span className="tracking-normal">
            Grounded in verbatim transcripts · Return to send, Shift+Return for newline
          </span>
          <span className="hidden sm:inline font-mono opacity-80">⌘N new chat · / focus</span>
        </div>
      </div>
    </div>
  );
};
