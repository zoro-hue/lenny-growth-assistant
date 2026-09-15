import { Session, Message, ModelOption } from '../types/chat';
import { Artifact } from '../types/artifact';

const API_BASE = 'http://localhost:8000';

export interface HealthStatus {
  status: string;
  database: string;
  dbDialect: string;
  version: string;
}

export const api = {
  async checkHealth(): Promise<HealthStatus | null> {
    try {
      const res = await fetch(`${API_BASE}/health`, {
        signal: AbortSignal.timeout(2000),
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  },

  async fetchModels(): Promise<ModelOption[] | null> {
    try {
      const res = await fetch(`${API_BASE}/api/models`, {
        signal: AbortSignal.timeout(3000),
      });
      if (!res.ok) return null;
      const data = await res.json();
      return (data.providers || []) as ModelOption[];
    } catch {
      return null;
    }
  },

  async fetchSessions(): Promise<Session[] | null> {
    try {
      const res = await fetch(`${API_BASE}/api/sessions`, {
        signal: AbortSignal.timeout(3000),
      });
      if (!res.ok) return null;
      const data = await res.json();
      // Map API response to frontend Session format
      return data.map((s: any) => ({
        id: s.id,
        title: s.title,
        createdAt: s.createdAt,
        updatedAt: s.updatedAt,
        activeModelId: s.activeModelId,
        messages: [],
        artifactIds: s.artifactIds || [],
      }));
    } catch {
      return null;
    }
  },

  async fetchSessionDetail(sessionId: string): Promise<{ messages: Message[]; artifacts: Artifact[] } | null> {
    try {
      const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`, {
        signal: AbortSignal.timeout(3000),
      });
      if (!res.ok) return null;
      const data = await res.json();
      return {
        messages: data.messages || [],
        artifacts: data.artifacts || [],
      };
    } catch {
      return null;
    }
  },

  async createSession(title: string = 'New conversation', activeModelId: string = 'openai-cloud'): Promise<Session | null> {
    try {
      const res = await fetch(`${API_BASE}/api/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, activeModelId }),
        signal: AbortSignal.timeout(3000),
      });
      if (!res.ok) return null;
      const s = await res.json();
      return {
        id: s.id,
        title: s.title,
        createdAt: s.createdAt,
        updatedAt: s.updatedAt,
        activeModelId: s.activeModelId,
        messages: [],
        artifactIds: s.artifactIds || [],
      };
    } catch {
      return null;
    }
  },

  async renameSession(sessionId: string, title: string): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
        signal: AbortSignal.timeout(3000),
      });
      return res.ok;
    } catch {
      return false;
    }
  },

  async deleteSession(sessionId: string): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`, {
        method: 'DELETE',
        signal: AbortSignal.timeout(3000),
      });
      return res.ok;
    } catch {
      return false;
    }
  },

  async updateSessionModel(sessionId: string, activeModelId: string): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activeModelId }),
        signal: AbortSignal.timeout(3000),
      });
      return res.ok;
    } catch {
      return false;
    }
  },

  async postMessage(sessionId: string, message: Partial<Message>): Promise<Message | null> {
    try {
      const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role: message.role,
          content: message.content,
          status: message.status || 'complete',
          citations: message.citations || [],
          artifactId: message.artifactId,
        }),
        signal: AbortSignal.timeout(3000),
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  },

  async sendChat(
    sessionId: string,
    content: string,
    modelId: string = 'openai-cloud',
    isEssay: boolean = false
  ): Promise<{
    userMessage: Message;
    assistantMessage: Message;
    artifact?: Artifact | null;
  } | null> {
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          content,
          modelId,
          isEssay,
        }),
        signal: AbortSignal.timeout(45000),
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  },

  async fetchKnowledgeStats(): Promise<any | null> {
    try {
      const res = await fetch(`${API_BASE}/api/knowledge/stats`, {
        signal: AbortSignal.timeout(3000),
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  },

  async searchKnowledge(query: string, topK: number = 3): Promise<any | null> {
    try {
      const res = await fetch(`${API_BASE}/api/knowledge/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, topK }),
        signal: AbortSignal.timeout(5000),
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  },
};
