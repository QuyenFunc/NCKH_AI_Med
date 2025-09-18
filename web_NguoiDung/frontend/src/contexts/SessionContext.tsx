import React, { createContext, useContext, useState, useCallback } from 'react';

interface SessionContextType {
  onSessionCreated: (callback: (sessionId: string) => void) => void;
  notifySessionCreated: (sessionId: string) => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

interface SessionProviderProps {
  children: React.ReactNode;
}

export const SessionProvider: React.FC<SessionProviderProps> = ({ children }) => {
  const [callbacks, setCallbacks] = useState<((sessionId: string) => void)[]>([]);

  const onSessionCreated = useCallback((callback: (sessionId: string) => void) => {
    setCallbacks(prev => [...prev, callback]);
  }, []);

  const notifySessionCreated = useCallback((sessionId: string) => {
    callbacks.forEach(callback => callback(sessionId));
  }, [callbacks]);

  return (
    <SessionContext.Provider value={{ onSessionCreated, notifySessionCreated }}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = (): SessionContextType => {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};
