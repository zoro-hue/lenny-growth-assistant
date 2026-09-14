import React, { useState } from 'react';
import { Check, Edit2, Trash2, X } from 'lucide-react';
import { Session } from '../../types/chat';

interface SessionListItemProps {
  session: Session;
  isActive: boolean;
  onSelect: (sessionId: string) => void;
  onRename: (sessionId: string, newTitle: string) => void;
  onDelete?: (sessionId: string) => void;
  isRailMode?: boolean;
}

export const SessionListItem: React.FC<SessionListItemProps> = ({
  session,
  isActive,
  onSelect,
  onRename,
  onDelete,
  isRailMode = false,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);
  const [titleInput, setTitleInput] = useState(session.title);

  const handleRenameSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    setIsEditing(false);
    if (titleInput.trim()) {
      onRename(session.id, titleInput.trim());
    } else {
      setTitleInput(session.title);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      setIsEditing(false);
      setTitleInput(session.title);
    }
  };

  // Format relative timestamp
  const formatTime = (isoString: string) => {
    const d = new Date(isoString);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (isRailMode) {
    return (
      <button
        type="button"
        onClick={() => onSelect(session.id)}
        title={session.title}
        aria-label={`Switch to session: ${session.title}`}
        className={`w-10 h-10 mx-auto my-1 rounded flex items-center justify-center font-sans text-xs transition-colors duration-fast relative group focus-visible:outline-evidence-600 ${
          isActive
            ? 'bg-paper-0 text-evidence-600 font-semibold border-l-2 border-evidence-600 shadow-xs'
            : 'text-ink-700 hover:bg-paper-200/80 hover:text-ink-950'
        }`}
      >
        <span className="truncate max-w-[28px] uppercase">
          {session.title.slice(0, 2)}
        </span>
      </button>
    );
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => onSelect(session.id)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect(session.id);
        }
      }}
      className={`group relative flex items-center justify-between px-3 py-2 cursor-pointer text-left transition-colors duration-fast select-none rounded-r focus-visible:outline-evidence-600 ${
        isActive
          ? 'bg-paper-0/90 text-ink-950 font-medium border-l-2 border-evidence-600 shadow-xs'
          : 'text-ink-700 hover:bg-paper-200/50 hover:text-ink-950 border-l-2 border-transparent'
      }`}
    >
      <div className="flex-1 min-w-0 pr-2">
        {isEditing ? (
          <form onSubmit={handleRenameSubmit} className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
            <input
              type="text"
              value={titleInput}
              onChange={(e) => setTitleInput(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={() => handleRenameSubmit()}
              autoFocus
              className="w-full text-xs font-sans px-1.5 py-0.5 bg-paper-0 border border-line-300 rounded outline-none focus:border-evidence-600 text-ink-950"
            />
            <button
              type="submit"
              className="p-1 text-evidence-600 hover:bg-paper-200 rounded"
              aria-label="Save title"
            >
              <Check className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => {
                setIsEditing(false);
                setTitleInput(session.title);
              }}
              className="p-1 text-ink-400 hover:text-ink-700 hover:bg-paper-200 rounded"
              aria-label="Cancel rename"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </form>
        ) : (
          <p className="text-xs sm:text-sm font-sans truncate leading-tight">
            {session.title}
          </p>
        )}
      </div>

      <div className="flex items-center gap-1 flex-shrink-0">
        {isConfirmingDelete ? (
          <div
            className="flex items-center gap-1 bg-signal-red-50 border border-signal-red-200 px-1.5 py-0.5 rounded shadow-xs"
            onClick={(e) => e.stopPropagation()}
          >
            <span className="text-[10px] font-sans font-medium text-signal-red-700">Delete?</span>
            <button
              type="button"
              onClick={() => {
                onDelete?.(session.id);
                setIsConfirmingDelete(false);
              }}
              title="Confirm delete session"
              aria-label="Confirm delete session"
              className="p-0.5 text-signal-red-700 hover:bg-signal-red-200 rounded transition-colors"
            >
              <Check className="w-3 h-3" />
            </button>
            <button
              type="button"
              onClick={() => setIsConfirmingDelete(false)}
              title="Cancel delete"
              aria-label="Cancel delete"
              className="p-0.5 text-ink-500 hover:bg-paper-200 rounded transition-colors"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        ) : !isEditing ? (
          <>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setTitleInput(session.title);
                setIsEditing(true);
              }}
              title="Rename chat"
              aria-label="Rename session"
              className="opacity-0 group-hover:opacity-100 p-1 text-ink-400 hover:text-ink-950 transition-opacity rounded hover:bg-paper-200"
            >
              <Edit2 className="w-3 h-3" />
            </button>
            {onDelete && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsConfirmingDelete(true);
                }}
                title="Delete chat"
                aria-label="Delete session"
                className="opacity-0 group-hover:opacity-100 p-1 text-ink-400 hover:text-signal-red-600 transition-opacity rounded hover:bg-signal-red-50"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            )}
            <span className="text-[11px] font-sans text-ink-500 font-normal">
              {formatTime(session.updatedAt || session.createdAt)}
            </span>
          </>
        ) : null}
      </div>
    </div>
  );
};
