import { useState, useCallback, useMemo, useEffect } from 'react';
import { Session, Message, SessionGroupType } from '../types/chat';
import { MOCK_SESSIONS } from '../data/mockData';
import { api } from '../services/api';

export function useSession() {
  const [sessions, setSessions] = useState<Session[]>(MOCK_SESSIONS);
  const [activeSessionId, setActiveSessionId] = useState<string>(() => {
    try {
      const saved = localStorage.getItem('lenny_active_session_id');
      if (saved) return saved;
    } catch {}
    return MOCK_SESSIONS[0].id;
  });

  // Sync with backend API if online
  useEffect(() => {
    let isMounted = true;
    async function syncWithBackend() {
      const health = await api.checkHealth();
      if (!health || !isMounted) return;

      const remoteSessions = await api.fetchSessions();
      if (remoteSessions && remoteSessions.length > 0 && isMounted) {
        // Check if previously saved session exists in remote sessions
        let targetId = remoteSessions[0].id;
        try {
          const savedId = localStorage.getItem('lenny_active_session_id');
          if (savedId && remoteSessions.some(s => s.id === savedId)) {
            targetId = savedId;
          }
        } catch {}

        // Fetch details for target active session
        const activeRemote = await api.fetchSessionDetail(targetId);
        const updatedRemote = remoteSessions.map(s => {
          if (s.id === targetId && activeRemote) {
            return {
              ...s,
              messages: activeRemote.messages || [],
              artifactIds: (activeRemote.artifacts || []).map(a => a.id),
            };
          }
          return s;
        });

        setSessions(updatedRemote);
        setActiveSessionId(targetId);
      }
    }
    syncWithBackend();
    return () => {
      isMounted = false;
    };
  }, []);

  const activeSession = useMemo(() => {
    return sessions.find(s => s.id === activeSessionId) || sessions[0];
  }, [sessions, activeSessionId]);

  const selectSession = useCallback(async (sessionId: string) => {
    setActiveSessionId(sessionId);
    try {
      localStorage.setItem('lenny_active_session_id', sessionId);
    } catch {}
    // Hydrate messages from backend if not yet loaded
    const targetSession = sessions.find(s => s.id === sessionId);
    if (!targetSession || targetSession.messages.length === 0) {
      try {
        const detail = await api.fetchSessionDetail(sessionId);
        if (detail) {
          setSessions(prev =>
            prev.map(s =>
              s.id === sessionId
                ? {
                    ...s,
                    messages: detail.messages || [],
                    artifactIds: (detail.artifacts || []).map(a => a.id),
                  }
                : s
            )
          );
        }
      } catch (err) {
        console.warn('Failed to load session detail:', err);
      }
    }
  }, [sessions]);

  const createNewSession = useCallback(async () => {
    let newId = 'session-' + Date.now();
    try {
      const remote = await api.createSession('New conversation', 'ollama-local');
      if (remote && remote.id) {
        newId = remote.id;
      }
    } catch (e) {
      console.warn('Backend createSession failed, falling back to local ID:', e);
    }
    const newSession: Session = {
      id: newId,
      title: 'New conversation',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      activeModelId: 'ollama-local',
      messages: [],
      artifactIds: [],
    };
    setSessions(prev => [newSession, ...prev.filter(s => s.id !== newId)]);
    setActiveSessionId(newId);
    try {
      localStorage.setItem('lenny_active_session_id', newId);
    } catch {}
    return newSession;
  }, []);

  const updateSessionTitle = useCallback((sessionId: string, newTitle: string) => {
    const trimmed = newTitle.trim() || 'Untitled';
    setSessions(prev =>
      prev.map(s => (s.id === sessionId ? { ...s, title: trimmed } : s))
    );
    // Sync to backend asynchronously
    api.renameSession(sessionId, trimmed).catch(() => {});
  }, []);

  const deleteSession = useCallback(async (sessionId: string) => {
    // Delete in backend asynchronously
    api.deleteSession(sessionId).catch(() => {});

    setSessions(prev => {
      const remaining = prev.filter(s => s.id !== sessionId);
      if (sessionId === activeSessionId) {
        if (remaining.length > 0) {
          const nextSession = remaining[0];
          setActiveSessionId(nextSession.id);
          // Hydrate if needed
          if (nextSession.messages.length === 0) {
            api.fetchSessionDetail(nextSession.id).then(detail => {
              if (detail) {
                setSessions(curr =>
                  curr.map(s =>
                    s.id === nextSession.id
                      ? { ...s, messages: detail.messages || [], artifactIds: (detail.artifacts || []).map(a => a.id) }
                      : s
                  )
                );
              }
            }).catch(() => {});
          }
        } else {
          // If no sessions remain, create a fresh one
          createNewSession();
        }
      }
      return remaining;
    });
  }, [activeSessionId, createNewSession]);

  const setSessionModel = useCallback((sessionId: string, modelId: string) => {
    setSessions(prev =>
      prev.map(s => (s.id === sessionId ? { ...s, activeModelId: modelId } : s))
    );
    // Persist active model to backend session via PATCH /api/sessions/{id}
    api.updateSessionModel(sessionId, modelId).catch(() => {});
  }, []);

  const addMessageToSession = useCallback((sessionId: string, message: Message) => {
    setSessions(prev =>
      prev.map(s => {
        if (s.id !== sessionId) return s;
        // Auto-generate title on first user message if title is 'New conversation'
        let title = s.title;
        if (s.messages.length === 0 && message.role === 'user') {
          const words = message.content.trim().split(/\s+/).slice(0, 6).join(' ');
          title = words.length > 0 ? words : 'New conversation';
        }
        return {
          ...s,
          title,
          updatedAt: new Date().toISOString(),
          messages: [...s.messages, message],
        };
      })
    );

    // Sync to backend asynchronously
    api.postMessage(sessionId, message).catch(() => {});
  }, []);

  const updateMessageInSession = useCallback(
    (sessionId: string, messageId: string, updates: Partial<Message>) => {
      setSessions(prev =>
        prev.map(s => {
          if (s.id !== sessionId) return s;
          return {
            ...s,
            messages: s.messages.map(m => (m.id === messageId ? { ...m, ...updates } : m)),
          };
        })
      );
    },
    []
  );

  const addArtifactToSession = useCallback((sessionId: string, artifactId: string) => {
    setSessions(prev =>
      prev.map(s => {
        if (s.id !== sessionId) return s;
        if (s.artifactIds.includes(artifactId)) return s;
        return {
          ...s,
          artifactIds: [...s.artifactIds, artifactId],
        };
      })
    );
  }, []);

  // Group sessions by relative dates per Spec Part B.2
  const groupedSessions = useMemo(() => {
    const groups: Record<SessionGroupType, Session[]> = {
      'Today': [],
      'Yesterday': [],
      'Previous 7 days': [],
      'Older': [],
    };

    const now = new Date();
    const todayMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterdayMidnight = new Date(todayMidnight.getTime() - 24 * 60 * 60 * 1000);
    const sevenDaysAgoMidnight = new Date(todayMidnight.getTime() - 7 * 24 * 60 * 60 * 1000);

    sessions.forEach(session => {
      const sessionDate = new Date(session.updatedAt || session.createdAt);
      if (sessionDate >= todayMidnight) {
        groups['Today'].push(session);
      } else if (sessionDate >= yesterdayMidnight) {
        groups['Yesterday'].push(session);
      } else if (sessionDate >= sevenDaysAgoMidnight) {
        groups['Previous 7 days'].push(session);
      } else {
        groups['Older'].push(session);
      }
    });

    return groups;
  }, [sessions]);

  return {
    sessions,
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
    addArtifactToSession,
    groupedSessions,
  };
}
