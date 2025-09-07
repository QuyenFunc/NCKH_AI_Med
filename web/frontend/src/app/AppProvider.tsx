import React from 'react';
import { AuthProvider } from '../contexts/AuthContext';
import { ChatProvider } from '../contexts/ChatContext';
import { ThemeProvider } from '../contexts/ThemeContext';

interface AppProviderProps {
  children: React.ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ChatProvider>
          {children}
        </ChatProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};
