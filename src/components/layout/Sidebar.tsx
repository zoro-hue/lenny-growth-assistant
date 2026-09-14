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
  isCollapsed?: boolean;
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
  isCollapsed = false,
  isMobileDrawer = false,
  onCloseDrawer,
  isLoadingSessions = false,
  onToggleCollapse,
}) => {
  const groups: SessionGroupType[] = ['Today', 'Yesterday', 'Previous 7 days', 'Older'];

  // When collapsed, render as icon rail mode
  const showAsRail = isCollapsed || isRailMode;

  return (
    <aside
      aria-label="Conversation History"
      className={`bg-paper-100 flex flex-col h-full select-none z-30 transition-all duration-300 ease-in-out flex-shrink-0 ${
        isMobileDrawer
          ? 'fixed inset-y-0 left-0 w-[280px] shadow-2xl z-50 border-r border-line-200'
          : isCollapsed
          ? 'w-0 border-r-0 overflow-hidden opacity-0 pointer-events-none'
          : 'w-[260px] border-r border-line-200 opacity-100'
      }`}
    >
      {/* Top Header / New Chat Action */}
      <div className="p-2.5 sm:p-3 border-b border-line-200/60 flex items-center justify-between gap-1.5">
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
                {!showAsRail && (
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
                      isRailMode={showAsRail}
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
      {!showAsRail && (
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
