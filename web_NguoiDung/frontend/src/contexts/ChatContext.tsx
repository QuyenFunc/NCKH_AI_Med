import React, { createContext, useContext } from 'react';
import { useChat as useOriginalChat } from '../hooks/useChat';
import { useSession } from './SessionContext';
import type { Message } from '../types';

interface ChatContextType {
  messages: Message[];
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  startNewSession: (forceNew?: boolean) => Promise<string | null>;
  loadExistingSession: (sessionId: string) => Promise<void>;
  clearError: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

interface ChatProviderProps {
  children: React.ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const { notifySessionCreated } = useSession();
  const chatState = useOriginalChat(notifySessionCreated);

  return (
    <ChatContext.Provider value={chatState}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
