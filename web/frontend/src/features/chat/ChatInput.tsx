import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import './styles/ChatInput.css';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading, disabled = false }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= 1000) {
      setMessage(value);
    }
    
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  useEffect(() => {
    if (textareaRef.current && !isLoading) {
      textareaRef.current.focus();
    }
  }, [isLoading]);

  const getCounterClass = () => {
    if (message.length > 900) return 'error';
    if (message.length > 800) return 'warning';
    return '';
  };

  return (
    <div className={`chat-input ${isLoading ? 'loading' : ''}`}>
      <div className="chat-input-container">
        <form onSubmit={handleSubmit} className="chat-input-form">
          <div className={`chat-input-wrapper ${disabled ? 'disabled' : ''}`}>
            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Mô tả triệu chứng của bạn..."
              disabled={isLoading || disabled}
              className="chat-textarea"
              rows={1}
            />
            
            <button
              type="submit"
              disabled={!message.trim() || isLoading || disabled}
              className="chat-send-button"
              aria-label="Gửi tin nhắn"
            >
              {isLoading ? (
                <Loader2 size={16} className="chat-send-spinner" />
              ) : (
                <Send size={16} />
              )}
            </button>
          </div>
          
          <div className="chat-input-meta">
            <div className="chat-input-help">
              Nhấn Enter để gửi, Shift + Enter để xuống dòng
            </div>
            <div className={`chat-input-counter ${getCounterClass()}`}>
              {message.length}/1000
            </div>
          </div>
        </form>
        
        {/* Disclaimer */}
        <div className="chat-disclaimer">
          <p className="chat-disclaimer-text">
            AI có thể đưa ra thông tin không chính xác. Hãy kiểm tra thông tin quan trọng với bác sĩ.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;