import React, { useState } from 'react';
import { Menu, PanelRight, Check, Edit2, FileText, PanelLeft, PanelLeftOpen, Plus } from 'lucide-react';
import { ModelOption } from '../../types/chat';
import { ModelProviderSelector } from './ModelProviderSelector';

interface ConversationHeaderProps {
  sessionTitle: string;
  onUpdateTitle: (newTitle: string) => void;
  activeModelId: string;
  onSelectModel: (model: ModelOption) => void;
  isArtifactViewerOpen: boolean;
  onToggleArtifactViewer: () => void;
  hasArtifacts: boolean;
  onOpenMobileDrawer?: () => void;
  showMobileMenuButton?: boolean;
  isModelSelectorOpen?: boolean;
  onToggleModelSelector?: () => void;
  onCloseModelSelector?: () => void;
  onToggleSidebar?: () => void;
  isSidebarCollapsed?: boolean;
  onNewChat?: () => void;
}

export const ConversationHeader: React.FC<ConversationHeaderProps> = ({
  sessionTitle,
  onUpdateTitle,
  activeModelId,
  onSelectModel,
  isArtifactViewerOpen,
  onToggleArtifactViewer,
  hasArtifacts,
  onOpenMobileDrawer,
  showMobileMenuButton = false,
  isModelSelectorOpen,
  onToggleModelSelector,
  onCloseModelSelector,
  onToggleSidebar,
  isSidebarCollapsed = false,
  onNewChat,
}) => {
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [titleInput, setTitleInput] = useState(sessionTitle);

  const handleTitleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    setIsEditingTitle(false);
    if (titleInput.trim()) {
      onUpdateTitle(titleInput.trim());
    } else {
      setTitleInput(sessionTitle);
    }
  };

  return (
    <header className="h-[56px] bg-paper-0 border-b border-line-200 px-3 sm:px-6 flex items-center justify-between gap-3 sm:gap-4 flex-shrink-0 z-10 select-none">
      {/* Left: Mobile Drawer Trigger / Sidebar Toggle + Editable Session Title */}
      <div className="flex items-center gap-2 min-w-0 flex-1">
        {showMobileMenuButton ? (
          <button
            type="button"
            onClick={onOpenMobileDrawer}
            aria-label="Open conversation sessions drawer"
            className="p-1.5 rounded text-ink-700 hover:text-ink-950 hover:bg-paper-100 transition-colors duration-fast focus-visible:outline-evidence-600"
          >
            <Menu className="w-5 h-5" />
          </button>
        ) : onToggleSidebar ? (
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={onToggleSidebar}
              title={isSidebarCollapsed ? "Expand sidebar (⌘B)" : "Collapse sidebar (⌘B)"}
              aria-label={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
              className="p-1.5 rounded text-ink-600 hover:text-ink-950 hover:bg-paper-100 transition-colors duration-fast focus-visible:outline-evidence-600"
            >
              {isSidebarCollapsed ? (
                <PanelLeftOpen className="w-4 h-4" />
              ) : (
                <PanelLeft className="w-4 h-4" />
              )}
            </button>
            {isSidebarCollapsed && onNewChat && (
              <button
                type="button"
                onClick={onNewChat}
                title="New chat (⌘N)"
                aria-label="New chat"
                className="p-1.5 rounded text-ink-600 hover:text-ink-950 hover:bg-paper-100 transition-colors duration-fast focus-visible:outline-evidence-600"
              >
                <Plus className="w-4 h-4" />
              </button>
            )}
          </div>
        ) : null}

        {isEditingTitle ? (
          <form onSubmit={handleTitleSubmit} className="flex items-center gap-1.5 max-w-md w-full">
            <input
              type="text"
              value={titleInput}
              onChange={(e) => setTitleInput(e.target.value)}
              onBlur={() => handleTitleSubmit()}
              autoFocus
              className="text-sm font-sans font-medium text-ink-950 bg-paper-100 border border-line-300 rounded px-2 py-1 w-full outline-none focus:border-evidence-600"
            />
            <button
              type="submit"
              aria-label="Save title"
              className="p-1 text-evidence-600 hover:bg-paper-200 rounded"
            >
              <Check className="w-4 h-4" />
            </button>
          </form>
        ) : (
          <div className="flex items-center gap-1.5 min-w-0 group">
            <h2 className="text-sm sm:text-base font-sans font-medium text-ink-950 truncate max-w-[280px] sm:max-w-md">
              {sessionTitle}
            </h2>
            <button
              type="button"
              onClick={() => {
                setTitleInput(sessionTitle);
                setIsEditingTitle(true);
              }}
              title="Click to rename session"
              aria-label="Rename session"
              className="opacity-0 group-hover:opacity-100 p-1 text-ink-500 hover:text-ink-950 rounded hover:bg-paper-100 transition-opacity focus-visible:opacity-100"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>

      {/* Right: Model Selector & Artifact Workbench Toggle */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <ModelProviderSelector
          activeModelId={activeModelId}
          onSelectModel={onSelectModel}
          isOpenExternal={isModelSelectorOpen}
          onToggleExternal={onToggleModelSelector}
          onCloseExternal={onCloseModelSelector}
        />

        <button
          type="button"
          onClick={onToggleArtifactViewer}
          aria-label={isArtifactViewerOpen ? "Close Artifact Workbench (⌘.)" : "Open Artifact Workbench (⌘.)"}
          title={isArtifactViewerOpen ? "Close Artifact Workbench (⌘.)" : "Open Artifact Workbench (⌘.)"}
          className={`relative p-2 rounded-md border transition-colors duration-fast flex items-center gap-1.5 text-xs font-sans font-medium focus-visible:outline-evidence-600 ${
            isArtifactViewerOpen
              ? 'bg-paper-200/80 border-line-300 text-ink-950'
              : hasArtifacts
              ? 'bg-paper-0 border-line-200 text-ink-950 hover:bg-paper-100'
              : 'bg-paper-0 border-line-200 text-ink-500 hover:text-ink-950 hover:bg-paper-100'
          }`}
        >
          {hasArtifacts ? (
            <FileText className="w-4 h-4 text-evidence-600" />
          ) : (
            <PanelRight className="w-4 h-4" />
          )}
          <span className="hidden md:inline">Workbench</span>
          {hasArtifacts && (
            <span
              className="w-1.5 h-1.5 rounded-full bg-evidence-600 absolute top-1 right-1"
              aria-hidden="true"
            />
          )}
        </button>
      </div>
    </header>
  );
};
