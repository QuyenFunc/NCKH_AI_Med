import React, { useEffect, useRef } from 'react';
import { MessageSquare, Loader2 } from 'lucide-react';
import Message from './Message';
import type { Message as MessageType } from '../../types';
import './styles/MessageList.css';

interface MessageListProps {
  messages: MessageType[];
  isLoading: boolean;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // ✅ Check if there's any streaming message
  const hasStreamingMessage = messages.some(msg => msg.isStreaming);

  // ✅ Only show typing indicator if loading AND no streaming message exists
  const shouldShowTypingIndicator = isLoading && !hasStreamingMessage;

  return (
    <div className="message-list">
      <div className="message-list-container">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        
        {shouldShowTypingIndicator && (
          <div className="typing-indicator">
            <div className="typing-avatar">
              <MessageSquare size={16} />
            </div>
            <div className="typing-dots">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageList;