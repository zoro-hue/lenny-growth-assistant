import React from 'react';
import { Plus, X, Radio, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { Session, SessionGroupType } from '../../types/chat';
import { SessionListItem } from './SessionListItem';

interface SidebarProps {
  groupedSessions: Record<SessionGroupType, Session[]>;
  activeSessionId: string;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  onRenameSession: (sessionId: string, newTitle: string) => void;
  onDeleteSession?: (sessionId: string) => void;
  isRailMode?: boolean;
  isMobileDrawer?: boolean;
  onCloseDrawer?: () => void;
  isLoadingSessions?: boolean;
  onToggleCollapse?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  groupedSessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onRenameSession,
  onDeleteSession,
  isRailMode = false,
  isMobileDrawer = false,
  onCloseDrawer,
  isLoadingSessions = false,
  onToggleCollapse,
}) => {
  const groups: SessionGroupType[] = ['Today', 'Yesterday', 'Previous 7 days', 'Older'];

  return (
    <aside
      aria-label="Conversation History"
      className={`bg-paper-100 border-r border-line-200 flex flex-col h-full select-none z-30 transition-all duration-300 ease-in-out ${
        isMobileDrawer
          ? 'fixed inset-y-0 left-0 w-[280px] shadow-2xl z-50'
          : isRailMode
          ? 'w-[56px]'
          : 'w-[240px]'
      }`}
    >
      {/* Top Header / New Chat Action */}
      <div className="p-2.5 sm:p-3 border-b border-line-200/60 flex items-center justify-between gap-1.5">
        {isRailMode ? (
          <div className="flex flex-col items-center gap-2 w-full">
            {onToggleCollapse && (
              <button
                type="button"
                onClick={onToggleCollapse}
                title="Expand sidebar (⌘B)"
                aria-label="Expand sidebar"
                className="w-10 h-8 rounded-md text-ink-600 hover:text-ink-950 hover:bg-paper-200 transition-colors duration-fast flex items-center justify-center focus-visible:outline-evidence-600"
              >
                <PanelLeftOpen className="w-4 h-4" />
              </button>
            )}
            <button
              type="button"
              onClick={onNewChat}
              title="New Chat (⌘N)"
              aria-label="New Chat"
              className="w-10 h-10 mx-auto rounded-md bg-paper-0 border border-line-200 text-ink-950 hover:bg-paper-200 transition-colors duration-fast flex items-center justify-center focus-visible:outline-evidence-600 shadow-xs"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <>
            <button
              type="button"
              onClick={() => {
                onNewChat();
                if (isMobileDrawer) onCloseDrawer?.();
              }}
              className="flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-pill bg-paper-0 border border-line-200 text-ink-950 font-sans text-sm font-medium hover:bg-paper-200/60 transition-colors duration-fast shadow-xs focus-visible:outline-evidence-600"
            >
              <Plus className="w-4 h-4 text-ink-700" />
              <span>New chat</span>
              <span className="text-[10px] font-mono text-ink-500 ml-auto hidden sm:inline">
                ⌘N
              </span>
            </button>

            {!isMobileDrawer && onToggleCollapse && (
              <button
                type="button"
                onClick={onToggleCollapse}
                title="Collapse sidebar (⌘B)"
                aria-label="Collapse sidebar"
                className="p-1.5 rounded-md text-ink-500 hover:text-ink-950 hover:bg-paper-200 transition-colors duration-fast flex-shrink-0 focus-visible:outline-evidence-600"
              >
                <PanelLeftClose className="w-4 h-4" />
              </button>
            )}

            {isMobileDrawer && (
              <button
                type="button"
                onClick={onCloseDrawer}
                aria-label="Close sidebar"
                className="p-1.5 rounded text-ink-500 hover:text-ink-950 hover:bg-paper-200 flex-shrink-0"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </>
        )}
      </div>

      {/* Session Groups List */}
      <div className="flex-1 overflow-y-auto py-2">
        {isLoadingSessions ? (
          /* Skeleton rows per Spec F.1: flat paper-200 bars, slow 800ms opacity pulse */
          <div className="px-3 space-y-3 pt-3 animate-pulse">
            <div className="h-3 bg-paper-200 rounded w-16 mb-2" />
            <div className="h-8 bg-paper-200 rounded" />
            <div className="h-8 bg-paper-200 rounded" />
            <div className="h-3 bg-paper-200 rounded w-20 mt-4 mb-2" />
            <div className="h-8 bg-paper-200 rounded" />
          </div>
        ) : (
          groups.map(group => {
            const sessions = groupedSessions[group];
            if (!sessions || sessions.length === 0) return null;

            return (
              <div key={group} className="mb-4">
                {/* Sentence case group title, no tracked-caps per Spec Part B.2 */}
                {!isRailMode && (
                  <div className="px-3 py-1 text-xs font-sans font-medium text-ink-500">
                    {group}
                  </div>
                )}
                <div className="space-y-0.5">
                  {sessions.map(session => (
                    <SessionListItem
                      key={session.id}
                      session={session}
                      isActive={session.id === activeSessionId}
                      isRailMode={isRailMode}
                      onSelect={id => {
                        onSelectSession(id);
                        if (isMobileDrawer) onCloseDrawer?.();
                      }}
                      onRename={onRenameSession}
                      onDelete={onDeleteSession}
                    />
                  ))}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      {!isRailMode && (
        <div className="p-3 border-t border-line-200 text-xs font-sans text-ink-500 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Radio className="w-3.5 h-3.5 text-evidence-600" />
            <span className="truncate">Lenny's Podcast Archive</span>
          </div>
          <span className="font-mono text-[11px] text-ink-500">v1.0</span>
        </div>
      )}
    </aside>
  );
};
