import React from 'react';

interface LoadingIndicatorProps {
  statusText?: string;
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  statusText = 'Retrieving transcripts…',
}) => {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex items-center gap-2.5 py-3 px-1 font-sans text-sm text-ink-500"
    >
      <span
        className="inline-block w-2 h-2 rounded-full bg-evidence-600 animate-pulse-dot"
        aria-hidden="true"
      />
      <span>{statusText}</span>
    </div>
  );
};
