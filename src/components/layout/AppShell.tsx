import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSession } from '../../hooks/useSession';
import { useArtifact } from '../../hooks/useArtifact';
import { useChatStream } from '../../hooks/useChatStream';
import { useToast } from '../common/Toaster';
import { Sidebar } from './Sidebar';
import { ConversationHeader } from './ConversationHeader';
import { ConversationPane } from '../chat/ConversationPane';
import { ArtifactViewer } from '../artifact/ArtifactViewer';
import { MODEL_OPTIONS } from '../../data/mockData';
import { ModelOption } from '../../types/chat';

export const AppShell: React.FC = () => {
  const { toast } = useToast();
  const composerTextareaRef = useRef<HTMLTextAreaElement>(null);

  // Viewport tracking for responsive layouts
  const [windowWidth, setWindowWidth] = useState<number>(
    typeof window !== 'undefined' ? window.innerWidth : 1440
  );
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState<boolean>(false);
  const [isModelSelectorOpen, setIsModelSelectorOpen] = useState<boolean>(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('lenny_sidebar_collapsed') === 'true';
    } catch {
      return false;
    }
  });

  const toggleSidebar = useCallback(() => {
    setIsSidebarCollapsed(prev => {
      const next = !prev;
      try {
        localStorage.setItem('lenny_sidebar_collapsed', String(next));
      } catch {}
      return next;
    });
  }, []);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isDesktopWide = windowWidth >= 1280;
  const isDesktopMedium = windowWidth >= 1024 && windowWidth < 1280;
  const isTablet = windowWidth >= 768 && windowWidth < 1024;
  const isMobile = windowWidth < 768;

  // Session state
  const {
    activeSession,
    activeSessionId,
    setActiveSessionId,
    selectSession,
    createNewSession,
    updateSessionTitle,
    deleteSession,
    setSessionModel,
    addMessageToSession,
    updateMessageInSession,
    removeMessageFromSession,
    addArtifactToSession,
    groupedSessions,
  } = useSession();

  // Artifact state for active session
  const {
    artifacts,
    activeArtifact,
    isViewerOpen,
    format,
    setFormat,
    currentSessionArtifacts,
    currentIndex,
    openArtifact,
    closeViewer,
    toggleViewer,
    nextArtifact,
    prevArtifact,
    updateArtifactTitle,
    toggleAllowScripts,
    addArtifact,
  } = useArtifact(activeSession?.artifactIds || []);

  // Chat stream state
  const { isStreaming, loadingStage, sendMessage } = useChatStream({
    sessionId: activeSessionId,
    activeModelId: activeSession?.activeModelId || 'openai-cloud',
    addMessage: addMessageToSession,
    updateMessage: updateMessageInSession,
    addArtifact,
    addArtifactToSession,
    openArtifactViewer: (artId: string) => {
      openArtifact(artId);
    },
  });

  const activeModel =
    MODEL_OPTIONS.find(m => m.id === activeSession?.activeModelId) || MODEL_OPTIONS[0];

  // Helper to find the user message before an error or the last user message
  const getLastUserPrompt = useCallback((failedMessageId?: string): string | null => {
    if (!activeSession || activeSession.messages.length === 0) return null;
    if (failedMessageId) {
      const errorIdx = activeSession.messages.findIndex(m => m.id === failedMessageId);
      if (errorIdx > 0) {
        for (let i = errorIdx - 1; i >= 0; i--) {
          if (activeSession.messages[i].role === 'user') {
            return activeSession.messages[i].content;
          }
        }
      }
    }
    const lastUser = [...activeSession.messages].reverse().find(m => m.role === 'user');
    return lastUser ? lastUser.content : null;
  }, [activeSession]);

  // Model switching with Spec E.5 system note
  const handleSelectModel = useCallback((model: ModelOption) => {
    if (activeSession && model.id !== activeSession.activeModelId) {
      setSessionModel(activeSessionId, model.id);
      const hasMessages = activeSession.messages.some(m => m.role === 'user' || m.role === 'assistant');
      if (hasMessages) {
        addMessageToSession(activeSessionId, {
          id: 'sys-' + Date.now(),
          role: 'system',
          content: `Switched to ${model.name} · ${model.provider}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        });
      }
      toast(`Active model changed to ${model.name}`, 'info');
    }
  }, [activeSession, activeSessionId, setSessionModel, addMessageToSession, toast]);

  const handleSwitchToCloud = useCallback((failedMessageId?: string) => {
    const cloudModel = MODEL_OPTIONS.find(m => m.provider === 'Cloud') || MODEL_OPTIONS[0];
    const targetModelId = cloudModel.id;

    if (activeSession && targetModelId !== activeSession.activeModelId) {
      setSessionModel(activeSessionId, targetModelId);
      addMessageToSession(activeSessionId, {
        id: 'sys-' + Date.now(),
        role: 'system',
        content: `Switched to ${cloudModel.name} · ${cloudModel.provider}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      });
      toast(`Switched to ${cloudModel.name} (Cloud)`, 'info');
    }

    if (failedMessageId) {
      removeMessageFromSession(activeSessionId, failedMessageId);
    }

    const promptToRetry = getLastUserPrompt(failedMessageId);
    if (promptToRetry) {
      const lower = promptToRetry.toLowerCase();
      const isEssay = lower.includes('essay') || lower.includes('ship 30');
      sendMessage(promptToRetry, isEssay, targetModelId, true);
    }
  }, [activeSession, activeSessionId, setSessionModel, addMessageToSession, removeMessageFromSession, getLastUserPrompt, sendMessage, toast]);

  const handleSwitchToLocal = useCallback((failedMessageId?: string) => {
    const localModel = MODEL_OPTIONS.find(m => m.provider === 'Local') || MODEL_OPTIONS[1];
    const targetModelId = localModel.id;

    if (activeSession && targetModelId !== activeSession.activeModelId) {
      setSessionModel(activeSessionId, targetModelId);
      addMessageToSession(activeSessionId, {
        id: 'sys-' + Date.now(),
        role: 'system',
        content: `Switched to ${localModel.name} · ${localModel.provider}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      });
      toast(`Switched to ${localModel.name} (Local)`, 'info');
    }

    if (failedMessageId) {
      removeMessageFromSession(activeSessionId, failedMessageId);
    }

    const promptToRetry = getLastUserPrompt(failedMessageId);
    if (promptToRetry) {
      const lower = promptToRetry.toLowerCase();
      const isEssay = lower.includes('essay') || lower.includes('ship 30');
      sendMessage(promptToRetry, isEssay, targetModelId, true);
    }
  }, [activeSession, activeSessionId, setSessionModel, addMessageToSession, removeMessageFromSession, getLastUserPrompt, sendMessage, toast]);

  const handleRetry = useCallback((failedMessageId?: string) => {
    if (failedMessageId) {
      removeMessageFromSession(activeSessionId, failedMessageId);
    }
    const promptToRetry = getLastUserPrompt(failedMessageId);
    if (promptToRetry) {
      const lower = promptToRetry.toLowerCase();
      const isEssay = lower.includes('essay') || lower.includes('ship 30');
      sendMessage(promptToRetry, isEssay, activeSession?.activeModelId, true);
    }
  }, [activeSession, activeSessionId, removeMessageFromSession, getLastUserPrompt, sendMessage]);

  // Global Keyboard Shortcuts (Part I)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isCmdOrCtrl = e.metaKey || e.ctrlKey;

      // Cmd/Ctrl + N -> New chat
      if (isCmdOrCtrl && e.key.toLowerCase() === 'n') {
        e.preventDefault();
        createNewSession();
        toast('New conversation started', 'info');
      }

      // Cmd/Ctrl + B -> Toggle Sidebar
      if (isCmdOrCtrl && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        toggleSidebar();
      }

      // Cmd/Ctrl + . -> Toggle Artifact Viewer
      if (isCmdOrCtrl && e.key === '.') {
        e.preventDefault();
        toggleViewer();
      }

      // Cmd/Ctrl + M -> Toggle Model Selector
      if (isCmdOrCtrl && e.key.toLowerCase() === 'm') {
        e.preventDefault();
        setIsModelSelectorOpen(prev => !prev);
      }

      // Esc -> Close viewer / modal / drawer
      if (e.key === 'Escape') {
        if (isViewerOpen) closeViewer();
        if (isMobileDrawerOpen) setIsMobileDrawerOpen(false);
        if (isModelSelectorOpen) setIsModelSelectorOpen(false);
      }

      // / -> Focus composer from anywhere (unless user is typing in another input)
      if (e.key === '/' && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
        e.preventDefault();
        composerTextareaRef.current?.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [createNewSession, toggleViewer, closeViewer, toggleSidebar, isViewerOpen, isMobileDrawerOpen, isModelSelectorOpen, toast]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-paper-0 font-sans text-ink-950 antialiased">
      {/* 1. Sidebar (Sessions Pane) */}
      {/* On desktop wide (>=1280px): 240px fixed or 56px when collapsed */}
      {/* On desktop medium (1024-1279px): 56px icon rail */}
      {/* On tablet and mobile (<1024px): hidden drawer toggleable by hamburger */}
      {!isTablet && !isMobile ? (
        <Sidebar
          groupedSessions={groupedSessions}
          activeSessionId={activeSessionId}
          onSelectSession={selectSession}
          onNewChat={createNewSession}
          onRenameSession={updateSessionTitle}
          onDeleteSession={(sessionId) => {
            deleteSession(sessionId);
            toast('Conversation deleted', 'info');
          }}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={toggleSidebar}
        />
      ) : (
        isMobileDrawerOpen && (
          <>
            {/* Backdrop overlay */}
            <div
              className="fixed inset-0 bg-ink-950/20 backdrop-blur-xs z-40"
              onClick={() => setIsMobileDrawerOpen(false)}
            />
            <Sidebar
              groupedSessions={groupedSessions}
              activeSessionId={activeSessionId}
              onSelectSession={selectSession}
              onNewChat={createNewSession}
              onRenameSession={updateSessionTitle}
              onDeleteSession={(sessionId) => {
                deleteSession(sessionId);
                toast('Conversation deleted', 'info');
              }}
              isMobileDrawer={true}
              onCloseDrawer={() => setIsMobileDrawerOpen(false)}
            />
          </>
        )
      )}

      {/* 2. Main Middle + Right Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden relative">
        {/* Header Bar: 56px height, spans conversation and workbench */}
        <ConversationHeader
          sessionTitle={activeSession?.title || 'New conversation'}
          onUpdateTitle={(newTitle) => updateSessionTitle(activeSessionId, newTitle)}
          activeModelId={activeSession?.activeModelId || 'openai-cloud'}
          onSelectModel={handleSelectModel}
          isArtifactViewerOpen={isViewerOpen}
          onToggleArtifactViewer={toggleViewer}
          hasArtifacts={(activeSession?.artifactIds?.length || 0) > 0}
          showMobileMenuButton={isTablet || isMobile}
          onOpenMobileDrawer={() => setIsMobileDrawerOpen(true)}
          isModelSelectorOpen={isModelSelectorOpen}
          onToggleModelSelector={() => setIsModelSelectorOpen(prev => !prev)}
          onCloseModelSelector={() => setIsModelSelectorOpen(false)}
          onToggleSidebar={toggleSidebar}
          isSidebarCollapsed={isSidebarCollapsed}
          onNewChat={createNewSession}
        />

        {/* Workspace Body: Conversation Pane + Artifact Viewer */}
        <div className="flex-1 flex min-h-0 overflow-hidden relative">
          {/* Conversation Pane (fluid, centered max 680px) */}
          <main className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
            <ConversationPane
              messages={activeSession?.messages || []}
              artifacts={artifacts}
              isStreaming={isStreaming}
              loadingStage={loadingStage}
              activeModel={activeModel}
              onSendMessage={sendMessage}
              onOpenArtifact={openArtifact}
              onOpenModelSelector={() => setIsModelSelectorOpen(true)}
              onSwitchToCloud={handleSwitchToCloud}
              onSwitchToLocal={handleSwitchToLocal}
              onRetry={handleRetry}
              textareaRef={composerTextareaRef}
            />
          </main>

          {/* 3. Artifact Viewer (collapsed by default, 440px when open) */}
          <ArtifactViewer
            artifact={activeArtifact}
            isOpen={isViewerOpen}
            format={format}
            onFormatChange={setFormat}
            onClose={closeViewer}
            onTitleChange={(newTitle) => {
              if (activeArtifact) updateArtifactTitle(activeArtifact.id, newTitle);
            }}
            onToggleAllowScripts={(artId) => toggleAllowScripts(artId)}
            totalArtifactsCount={currentSessionArtifacts.length}
            currentIndex={currentIndex}
            onNextArtifact={nextArtifact}
            onPrevArtifact={prevArtifact}
            onCopySuccess={() => toast('Document content copied to clipboard', 'success')}
            isMobileOverlay={isMobile || isTablet}
          />
        </div>
      </div>
    </div>
  );
};
