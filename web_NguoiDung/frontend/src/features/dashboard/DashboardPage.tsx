import React from 'react';
import { ChatWindow } from '../chat';
import { useChat } from '../../contexts/ChatContext';

const DashboardPage: React.FC = () => {
  const { 
    messages, 
    sessionId, 
    isLoading, 
    sendMessage, 
    startNewSession 
  } = useChat();

  return (
    <ChatWindow
      messages={messages}
      isLoading={isLoading}
      onSendMessage={sendMessage}
      onNewChat={startNewSession}
      sessionId={sessionId}
    />
  );
};

export default DashboardPage;
