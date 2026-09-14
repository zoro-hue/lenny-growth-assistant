export type ArtifactFormat = 'rendered' | 'source';

export type ArtifactType = 'markdown' | 'html';

export interface Artifact {
  id: string;
  sessionId: string;
  title: string;
  type: ArtifactType;
  content: string;
  wordCount: number;
  sourceCount: number;
  createdAt: string;
  allowScripts?: boolean;
}
