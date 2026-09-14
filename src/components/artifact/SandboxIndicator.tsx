import React from 'react';
import { ShieldCheck, ShieldAlert } from 'lucide-react';

interface SandboxIndicatorProps {
  allowScripts: boolean;
  onToggleScripts: () => void;
}

export const SandboxIndicator: React.FC<SandboxIndicatorProps> = ({
  allowScripts,
  onToggleScripts,
}) => {
  return (
    <div className="bg-paper-100 border-b border-line-200 px-4 py-2 flex items-center justify-between gap-3 text-xs font-sans text-ink-700">
      <div className="flex items-center gap-2">
        {allowScripts ? (
          <ShieldAlert className="w-3.5 h-3.5 text-signal-amber-600 flex-shrink-0" />
        ) : (
          <ShieldCheck className="w-3.5 h-3.5 text-evidence-600 flex-shrink-0" />
        )}
        <span>
          {allowScripts
            ? 'Interactive scripts enabled in sandbox'
            : 'Sandboxed preview — scripts disabled'}
        </span>
      </div>

      <button
        type="button"
        onClick={onToggleScripts}
        className="text-[11px] font-medium text-ink-950 underline underline-offset-2 hover:text-evidence-600 focus-visible:outline-evidence-600"
      >
        {allowScripts ? 'Disable scripts' : 'Enable interactivity'}
      </button>
    </div>
  );
};
