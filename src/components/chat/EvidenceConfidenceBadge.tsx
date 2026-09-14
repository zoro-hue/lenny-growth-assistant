import React from 'react';
import { AlertCircle } from 'lucide-react';

interface EvidenceConfidenceBadgeProps {
  label?: string;
}

export const EvidenceConfidenceBadge: React.FC<EvidenceConfidenceBadgeProps> = ({
  label = 'Insufficient Grounded Evidence in Archives',
}) => {
  return (
    <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-sans font-medium text-signal-amber-600 bg-signal-amber-100 mb-3 select-none">
      <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
      <span>{label}</span>
    </div>
  );
};
