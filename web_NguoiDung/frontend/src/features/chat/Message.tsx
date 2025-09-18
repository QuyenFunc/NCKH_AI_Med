import React from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot, AlertTriangle, AlertCircle, Clock, Target, ExternalLink, Loader } from 'lucide-react';
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
          
          {/* Streaming Indicator */}
          {message.isStreaming && (
            <div className="message-status streaming">
              <Loader size={12} className="spinning" />
              <span>Đang trả lời...</span>
            </div>
          )}
          
          {/* Emergency/Warning Status */}
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

        {/* Chat Metadata (for assistant messages) */}
        {!isUser && message.metadata && !message.isStreaming && (
          <div className="message-metadata">
            {/* Confidence Score */}
            {message.metadata.confidence !== undefined && (
              <div className="metadata-item confidence">
                <Target size={12} />
                <span>Độ tin cậy: {Math.round(message.metadata.confidence * 100)}%</span>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill" 
                    style={{ width: `${message.metadata.confidence * 100}%` }}
                  />
                </div>
              </div>
            )}

            {/* Sources */}
            {message.metadata.sources && message.metadata.sources.length > 0 && (
              <div className="metadata-sources">
                <h4>Nguồn tham khảo:</h4>
                <div className="sources-list">
                  {message.metadata.sources.slice(0, 3).map((source, index) => (
                    <div key={index} className="source-item">
                      <div className="source-title">
                        <ExternalLink size={12} />
                        <span>{source.title}</span>
                        {source.confidence && (
                          <span className="source-confidence">
                            ({Math.round(source.confidence * 100)}%)
                          </span>
                        )}
                      </div>
                      {source.content && (
                        <div className="source-content">
                          {source.content.length > 200 
                            ? `${source.content.substring(0, 200)}...` 
                            : source.content
                          }
                        </div>
                      )}
                      {source.url && (
                        <a 
                          href={source.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="source-link"
                        >
                          Xem chi tiết
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;