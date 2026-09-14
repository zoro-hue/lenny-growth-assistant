import React, { createContext, useContext, useState, useCallback } from 'react';
import { X, CheckCircle2, AlertTriangle, Info } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
}

interface ToastContextType {
  toast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback((message: string, type: ToastType = 'info') => {
    const id = 'toast-' + Date.now();
    setToasts(prev => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3200);
  }, []);

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div
        aria-live="polite"
        className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none"
      >
        {toasts.map(t => (
          <div
            key={t.id}
            role="status"
            className="pointer-events-auto flex items-center gap-2.5 px-3.5 py-2.5 bg-ink-950 text-paper-0 text-sm font-sans rounded-md shadow-md border border-line-300 animate-chip-in max-w-sm"
          >
            {t.type === 'success' && <CheckCircle2 className="w-4 h-4 text-evidence-100 flex-shrink-0" />}
            {t.type === 'error' && <AlertTriangle className="w-4 h-4 text-signal-amber-100 flex-shrink-0" />}
            {t.type === 'info' && <Info className="w-4 h-4 text-paper-200 flex-shrink-0" />}
            <span className="flex-1">{t.message}</span>
            <button
              onClick={() => removeToast(t.id)}
              className="text-paper-200 hover:text-paper-0 p-0.5"
              aria-label="Dismiss notification"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};
