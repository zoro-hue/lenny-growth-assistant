export type ModelProviderType = 'cloud' | 'local';

export interface ModelOption {
  id: string;
  name: string;
  provider: 'Cloud' | 'Local';
  note: string;
  available: boolean;
  modelIdentifier: string;
}

export interface Citation {
  id: string;
  episodeNumber?: number;
  episodeTitle: string;
  guest: string;
  guestRole?: string;
  timestamp: string;
  quoteExcerpt: string;
  episodeUrl: string;
  relevanceScore?: number;
  whyThisSource?: string;
}

export type MessageStatus = 'streaming' | 'complete' | 'low-evidence' | 'error';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  status?: MessageStatus;
  citations?: Citation[];
  artifactId?: string;
  errorDetails?: {
    message: string;
    canSwitchToCloud?: boolean;
  };
  evidenceStrength?: 'high' | 'limited' | 'not-grounded';
  evidenceLabel?: string;
  followUpSuggestions?: string[];
}

export type SessionGroupType = 'Today' | 'Yesterday' | 'Previous 7 days' | 'Older';

export interface Session {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  activeModelId: string;
  messages: Message[];
  artifactIds: string[];
}
