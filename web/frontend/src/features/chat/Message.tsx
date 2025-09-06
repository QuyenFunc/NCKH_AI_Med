import React from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot, AlertTriangle, AlertCircle, Clock } from 'lucide-react';
import type { Message as MessageType } from '../../types';
import './styles/Message.css';

interface MessageProps {
  message: MessageType;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  // Kiểm tra nội dung có từ khóa khẩn cấp hay không
  const hasEmergency = /KHẨN CẤP|EMERGENCY|CẤP CỨU/i.test(message.content);
  const hasWarning = /CẢNH BÁO|WARNING|CHÚ Ý|LƯU Ý/i.test(message.content);

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getContentClass = () => {
    if (hasEmergency) return 'emergency';
    if (hasWarning) return 'warning';
    return '';
  };

  return (
    <div className={`message ${isUser ? 'user' : 'assistant'}`}>
      {/* Avatar */}
      <div className={`message-avatar ${isUser ? 'user' : 'assistant'}`}>
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>

      {/* Message Bubble */}
      <div className="message-bubble">
        <div className={`message-content ${getContentClass()}`}>
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <ReactMarkdown
              components={{
                // Custom component rendering for better styling
                p: ({ children }) => <p>{children}</p>,
                strong: ({ children }) => <strong>{children}</strong>,
                em: ({ children }) => <em>{children}</em>,
                code: ({ children }) => <code>{children}</code>,
                pre: ({ children }) => <pre>{children}</pre>,
                ul: ({ children }) => <ul>{children}</ul>,
                ol: ({ children }) => <ol>{children}</ol>,
                li: ({ children }) => <li>{children}</li>,
                blockquote: ({ children }) => <blockquote>{children}</blockquote>,
                h1: ({ children }) => <h1>{children}</h1>,
                h2: ({ children }) => <h2>{children}</h2>,
                h3: ({ children }) => <h3>{children}</h3>,
                h4: ({ children }) => <h4>{children}</h4>,
                h5: ({ children }) => <h5>{children}</h5>,
                h6: ({ children }) => <h6>{children}</h6>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Message Meta */}
        <div className="message-meta">
          <div className="message-timestamp">
            <Clock size={12} />
            <span>{formatTimestamp(message.timestamp)}</span>
          </div>
          
          {(hasEmergency || hasWarning) && (
            <div className="message-status">
              {hasEmergency ? (
                <AlertCircle size={12} className="status-icon emergency" />
              ) : (
                <AlertTriangle size={12} className="status-icon warning" />
              )}
              <span>{hasEmergency ? 'Khẩn cấp' : 'Cảnh báo'}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Message;