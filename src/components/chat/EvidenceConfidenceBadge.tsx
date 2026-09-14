import React from 'react';
import { AlertCircle, CheckCircle2, FileText } from 'lucide-react';

interface EvidenceConfidenceBadgeProps {
  type?: 'high' | 'limited' | 'not-grounded';
  label?: string;
}

export const EvidenceConfidenceBadge: React.FC<EvidenceConfidenceBadgeProps> = ({
  type = 'not-grounded',
  label,
}) => {
  if (type === 'high') {
    return (
      <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-sans font-medium text-evidence-700 bg-evidence-100/80 mb-3 select-none border border-evidence-600/20">
        <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0 text-evidence-600" />
        <span className="font-semibold tracking-wide uppercase text-[10px]">HIGH EVIDENCE</span>
        <span className="text-ink-500">·</span>
        <span className="text-ink-700 font-normal">{label || '3 transcript sources · 2 speakers'}</span>
      </div>
    );
  }

  if (type === 'limited') {
    return (
      <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-sans font-medium text-signal-amber-700 bg-signal-amber-100/80 mb-3 select-none border border-signal-amber-600/20">
        <FileText className="w-3.5 h-3.5 flex-shrink-0 text-signal-amber-600" />
        <span className="font-semibold tracking-wide uppercase text-[10px]">LIMITED EVIDENCE</span>
        <span className="text-ink-500">·</span>
        <span className="text-ink-700 font-normal">{label || '1 relevant transcript source'}</span>
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-sans font-medium text-signal-amber-800 bg-signal-amber-100 mb-3 select-none border border-signal-amber-600/20">
      <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 text-signal-amber-600" />
      <span className="font-semibold tracking-wide uppercase text-[10px]">NOT GROUNDED</span>
      <span className="text-ink-500">·</span>
      <span className="text-ink-700 font-normal">{label || 'No supporting Lenny Podcast evidence found'}</span>
    </div>
  );
};
