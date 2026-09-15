import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check, Server, Cloud, AlertCircle } from 'lucide-react';
import { ModelOption } from '../../types/chat';
import { MODEL_OPTIONS } from '../../data/mockData';
import { api } from '../../services/api';

interface ModelProviderSelectorProps {
  activeModelId: string;
  onSelectModel: (model: ModelOption) => void;
  isOpenExternal?: boolean;
  onToggleExternal?: () => void;
  onCloseExternal?: () => void;
}

export const ModelProviderSelector: React.FC<ModelProviderSelectorProps> = ({
  activeModelId,
  onSelectModel,
  isOpenExternal,
  onToggleExternal,
  onCloseExternal,
}) => {
  const [models, setModels] = useState<ModelOption[]>(MODEL_OPTIONS);
  const [isOpenInternal, setIsOpenInternal] = useState(false);
  const isOpen = isOpenExternal !== undefined ? isOpenExternal : isOpenInternal;

  const handleToggle = () => {
    if (onToggleExternal) {
      onToggleExternal();
    } else {
      setIsOpenInternal(prev => !prev);
    }
  };

  const handleClose = () => {
    if (onCloseExternal) {
      onCloseExternal();
    }
    setIsOpenInternal(false);
  };

  const containerRef = useRef<HTMLDivElement>(null);

  // Dynamically fetch model availability from backend
  useEffect(() => {
    let isMounted = true;
    async function loadModels() {
      try {
        const fetched = await api.fetchModels();
        if (fetched && fetched.length > 0 && isMounted) {
          setModels(fetched);
        }
      } catch {
        // Fallback to local MODEL_OPTIONS
      }
    }
    loadModels();
    return () => {
      isMounted = false;
    };
  }, []);

  const activeModel = models.find(m => m.id === activeModelId) || models[0] || MODEL_OPTIONS[0];

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        handleClose();
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const cloudModels = models.filter(m => m.provider === 'Cloud');
  const localModels = models.filter(m => m.provider === 'Local');

  const handleSelect = (model: ModelOption) => {
    onSelectModel(model);
    handleClose();
  };

  const isOllama = activeModel.provider === 'Local';
  const triggerLabel = isOllama
    ? activeModel.available
      ? 'Ollama · Local'
      : 'Ollama · Offline'
    : activeModel.available
    ? 'OpenAI · Cloud'
    : 'OpenAI · Key Required';

  return (
    <div className="relative inline-block text-left" ref={containerRef}>
      {/* Header Chip Trigger matching Section 17 & 18 */}
      <button
        type="button"
        onClick={handleToggle}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-label={`Current model: ${triggerLabel}. Click to switch model.`}
        className="inline-flex items-center gap-2 px-2.5 py-1.5 rounded-md border border-line-200 bg-paper-0 hover:bg-paper-100 hover:border-line-300 text-ink-950 font-sans text-xs sm:text-sm font-medium transition-all duration-150 shadow-xs focus-visible:outline-evidence-600"
      >
        <span
          className={`w-2 h-2 rounded-full flex-shrink-0 transition-colors ${
            activeModel.available
              ? 'bg-evidence-600'
              : 'border border-signal-amber-600 bg-transparent'
          }`}
        />
        <span className="font-mono text-xs">{triggerLabel}</span>
        <ChevronDown className="w-3.5 h-3.5 text-ink-500 ml-0.5" />
      </button>

      {/* Popover */}
      {isOpen && (
        <div
          role="menu"
          aria-orientation="vertical"
          className="absolute right-0 mt-1.5 w-76 origin-top-right rounded-md bg-paper-0 border border-line-200 shadow-lg z-50 animate-chip-in p-2 text-ink-950"
        >
          {/* Popover Header */}
          <div className="px-2 py-1 mb-1 text-[10px] font-mono uppercase tracking-widest text-ink-500 font-bold border-b border-line-200/80">
            MODELS
          </div>

          {/* Local / Ollama Group */}
          <div className="space-y-1 mb-2">
            {localModels.map(model => (
              <button
                key={model.id}
                type="button"
                role="menuitem"
                onClick={() => handleSelect(model)}
                className={`w-full text-left px-2.5 py-2 rounded text-xs transition-colors duration-150 flex items-start justify-between group ${
                  model.id === activeModelId
                    ? 'bg-paper-100 text-ink-950 font-medium'
                    : 'hover:bg-paper-100/70 text-ink-950'
                }`}
              >
                <div className="flex items-start gap-2 min-w-0 flex-1">
                  <span
                    className={`w-2 h-2 rounded-full flex-shrink-0 mt-1.5 ${
                      model.id === activeModelId && model.available
                        ? 'bg-evidence-600'
                        : model.available
                        ? 'border border-ink-400 bg-transparent'
                        : 'border border-signal-amber-600 bg-transparent'
                    }`}
                  />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-1">
                      <span className="font-semibold text-ink-950">Ollama</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-paper-200/70 text-ink-700">
                        Local
                      </span>
                    </div>
                    <div className="text-[11px] text-ink-600 font-mono mt-0.5">
                      {model.name.replace('Ollama ', '')}
                    </div>
                    {!model.available && (
                      <span className="inline-flex items-center gap-0.5 text-[10px] text-signal-amber-700 mt-0.5">
                        <AlertCircle className="w-2.5 h-2.5" />
                        <span>Offline (localhost:11434)</span>
                      </span>
                    )}
                  </div>
                </div>
                {model.id === activeModelId && (
                  <Check className="w-4 h-4 text-evidence-600 flex-shrink-0 mt-0.5 ml-1" />
                )}
              </button>
            ))}
          </div>

          <div className="border-t border-line-200 my-1" />

          {/* Cloud / OpenAI Group */}
          <div className="space-y-1">
            {cloudModels.map(model => (
              <button
                key={model.id}
                type="button"
                role="menuitem"
                onClick={() => handleSelect(model)}
                className={`w-full text-left px-2.5 py-2 rounded text-xs transition-colors duration-150 flex items-start justify-between group ${
                  model.id === activeModelId
                    ? 'bg-paper-100 text-ink-950 font-medium'
                    : 'hover:bg-paper-100/70 text-ink-950'
                }`}
              >
                <div className="flex items-start gap-2 min-w-0 flex-1">
                  <span
                    className={`w-2 h-2 rounded-full flex-shrink-0 mt-1.5 ${
                      model.id === activeModelId && model.available
                        ? 'bg-evidence-600'
                        : model.available
                        ? 'border border-ink-400 bg-transparent'
                        : 'border border-signal-amber-600 bg-transparent'
                    }`}
                  />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-1">
                      <span className="font-semibold text-ink-950">OpenAI</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-paper-200/70 text-ink-700">
                        Cloud
                      </span>
                    </div>
                    <div className="text-[11px] text-ink-600 font-mono mt-0.5">
                      {model.name.replace('OpenAI ', '')}
                    </div>
                    {!model.available && (
                      <span className="inline-flex items-center gap-0.5 text-[10px] text-signal-amber-700 mt-0.5">
                        <AlertCircle className="w-2.5 h-2.5" />
                        <span>API key required</span>
                      </span>
                    )}
                  </div>
                </div>
                {model.id === activeModelId && (
                  <Check className="w-4 h-4 text-evidence-600 flex-shrink-0 mt-0.5 ml-1" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
