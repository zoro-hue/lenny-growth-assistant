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

  return (
    <div className="relative inline-block text-left" ref={containerRef}>
      {/* Header Chip Trigger */}
      <button
        type="button"
        onClick={handleToggle}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-label={`Current model: ${activeModel.modelIdentifier || activeModel.name}. Click to switch model.`}
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-md border border-line-200 bg-paper-0 hover:bg-paper-100 text-ink-950 font-sans text-xs sm:text-sm font-medium transition-colors duration-fast focus-visible:outline-evidence-600"
      >
        <span
          className={`w-2 h-2 rounded-full flex-shrink-0 ${
            activeModel.available ? 'bg-evidence-600' : 'bg-signal-amber-600'
          }`}
        />
        <span className="truncate">{activeModel.modelIdentifier || activeModel.name}</span>
        <ChevronDown className="w-3.5 h-3.5 text-ink-500 ml-0.5" />
      </button>

      {/* Popover */}
      {isOpen && (
        <div
          role="menu"
          aria-orientation="vertical"
          className="absolute right-0 mt-1.5 w-80 origin-top-right rounded-md bg-paper-0 border border-line-200 shadow-lg ring-1 ring-black/5 z-50 animate-chip-in p-1.5 text-ink-950"
        >
          {/* Cloud Group */}
          <div className="px-2 py-1 text-[11px] font-mono text-ink-500 uppercase tracking-wider flex items-center gap-1.5">
            <Cloud className="w-3 h-3 text-ink-500" />
            <span>Cloud Providers (OpenAI)</span>
          </div>
          <div className="space-y-0.5 mb-2">
            {cloudModels.map(model => (
              <button
                key={model.id}
                type="button"
                role="menuitem"
                onClick={() => handleSelect(model)}
                className={`w-full text-left px-2.5 py-2 rounded text-xs transition-colors duration-fast flex items-start justify-between group ${
                  model.id === activeModelId
                    ? 'bg-paper-100 text-ink-950 font-medium'
                    : 'hover:bg-paper-100 text-ink-950'
                }`}
              >
                <div className="pr-2 min-w-0 flex-1">
                  <div className="flex items-center gap-1.5">
                    <span className="font-medium truncate">{model.name}</span>
                    {!model.available && (
                      <span
                        title="API key missing — requests will display error state"
                        className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] bg-signal-amber-100 text-signal-amber-800"
                      >
                        <AlertCircle className="w-2.5 h-2.5" />
                        <span>Key Required</span>
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-ink-500 mt-0.5 leading-snug">{model.note}</div>
                </div>
                {model.id === activeModelId && (
                  <Check className="w-4 h-4 text-evidence-600 flex-shrink-0 mt-0.5" />
                )}
              </button>
            ))}
          </div>

          <div className="border-t border-line-200 my-1" />

          {/* Local Group */}
          <div className="px-2 py-1 text-[11px] font-mono text-ink-500 uppercase tracking-wider flex items-center gap-1.5">
            <Server className="w-3 h-3 text-ink-500" />
            <span>Local Providers (Ollama)</span>
          </div>
          <div className="space-y-0.5">
            {localModels.map(model => (
              <button
                key={model.id}
                type="button"
                role="menuitem"
                onClick={() => handleSelect(model)}
                className={`w-full text-left px-2.5 py-2 rounded text-xs transition-colors duration-fast flex items-start justify-between group ${
                  !model.available
                    ? 'opacity-60 text-ink-500'
                    : model.id === activeModelId
                    ? 'bg-paper-100 text-ink-950 font-medium'
                    : 'hover:bg-paper-100 text-ink-950'
                }`}
              >
                <div className="pr-2 min-w-0 flex-1">
                  <div className="flex items-center gap-1.5">
                    <span className="font-medium truncate">{model.name}</span>
                    {model.available ? (
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] bg-evidence-100 text-evidence-800">
                        Online
                      </span>
                    ) : (
                      <span
                        title="Ollama server offline on localhost:11434"
                        className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] bg-signal-amber-100 text-signal-amber-800"
                      >
                        <AlertCircle className="w-2.5 h-2.5" />
                        <span>Offline</span>
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-ink-500 mt-0.5 leading-snug">{model.note}</div>
                </div>
                {model.id === activeModelId && (
                  <Check className="w-4 h-4 text-evidence-600 flex-shrink-0 mt-0.5" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
