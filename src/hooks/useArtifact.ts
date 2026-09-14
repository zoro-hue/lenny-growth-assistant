import { useState, useCallback, useMemo } from 'react';
import { Artifact, ArtifactFormat } from '../types/artifact';
import { MOCK_ARTIFACTS } from '../data/mockData';

export function useArtifact(sessionArtifactIds: string[] = []) {
  const [artifacts, setArtifacts] = useState<Record<string, Artifact>>(MOCK_ARTIFACTS);
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(
    sessionArtifactIds[0] || 'artifact-1'
  );
  const [isViewerOpen, setIsViewerOpen] = useState<boolean>(false);
  const [format, setFormat] = useState<ArtifactFormat>('rendered');

  const activeArtifact = useMemo(() => {
    if (!activeArtifactId) return null;
    return artifacts[activeArtifactId] || null;
  }, [artifacts, activeArtifactId]);

  // Session artifacts list for the stepper navigation < 1/3 >
  const currentSessionArtifacts = useMemo(() => {
    return sessionArtifactIds
      .map(id => artifacts[id])
      .filter((a): a is Artifact => Boolean(a));
  }, [sessionArtifactIds, artifacts]);

  const currentIndex = useMemo(() => {
    if (!activeArtifactId) return 0;
    const idx = currentSessionArtifacts.findIndex(a => a.id === activeArtifactId);
    return idx >= 0 ? idx : 0;
  }, [currentSessionArtifacts, activeArtifactId]);

  const openArtifact = useCallback((artifactId: string) => {
    setActiveArtifactId(artifactId);
    setIsViewerOpen(true);
    setFormat('rendered');
  }, []);

  const closeViewer = useCallback(() => {
    setIsViewerOpen(false);
  }, []);

  const toggleViewer = useCallback(() => {
    setIsViewerOpen(prev => !prev);
  }, []);

  const nextArtifact = useCallback(() => {
    if (currentIndex < currentSessionArtifacts.length - 1) {
      setActiveArtifactId(currentSessionArtifacts[currentIndex + 1].id);
    }
  }, [currentIndex, currentSessionArtifacts]);

  const prevArtifact = useCallback(() => {
    if (currentIndex > 0) {
      setActiveArtifactId(currentSessionArtifacts[currentIndex - 1].id);
    }
  }, [currentIndex, currentSessionArtifacts]);

  const updateArtifactTitle = useCallback((artifactId: string, title: string) => {
    setArtifacts(prev => {
      const art = prev[artifactId];
      if (!art) return prev;
      return {
        ...prev,
        [artifactId]: { ...art, title },
      };
    });
  }, []);

  const toggleAllowScripts = useCallback((artifactId: string) => {
    setArtifacts(prev => {
      const art = prev[artifactId];
      if (!art) return prev;
      return {
        ...prev,
        [artifactId]: { ...art, allowScripts: !art.allowScripts },
      };
    });
  }, []);

  const addArtifact = useCallback((artifact: Artifact) => {
    setArtifacts(prev => ({
      ...prev,
      [artifact.id]: artifact,
    }));
    setActiveArtifactId(artifact.id);
    setIsViewerOpen(true);
  }, []);

  return {
    artifacts,
    activeArtifact,
    activeArtifactId,
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
  };
}
