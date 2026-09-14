import React from 'react';
import { ToastProvider } from './components/common/Toaster';
import { AppShell } from './components/layout/AppShell';

export const App: React.FC = () => {
  return (
    <ToastProvider>
      <AppShell />
    </ToastProvider>
  );
};

export default App;
