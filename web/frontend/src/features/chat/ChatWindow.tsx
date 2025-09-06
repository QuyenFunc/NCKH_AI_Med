import React from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import type { Message } from '../../types';
import './styles/ChatWindow.css';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  onNewChat: () => void;
  sessionId: string | null;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onNewChat,
  sessionId
}) => {
  return (
    <div className="chat-window">
      {/* Welcome Screen */}
      {messages.length === 0 && (
        <div className="welcome-screen">
          <div className="welcome-content">
            {/* <div className="welcome-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19.5 3h-3.09A4.47 4.47 0 0 0 12 0a4.47 4.47 0 0 0-4.41 3H4.5A1.5 1.5 0 0 0 3 4.5v16A1.5 1.5 0 0 0 4.5 22h15a1.5 1.5 0 0 0 1.5-1.5v-16A1.5 1.5 0 0 0 19.5 3zM12 1.5a3 3 0 0 1 2.816 2H9.184A3 3 0 0 1 12 1.5zm7.5 19.5h-15v-16h2.25V6.5a.75.75 0 0 0 1.5 0V4.5h6.5V6.5a.75.75 0 0 0 1.5 0V4.5h2.25v16z"/>
                <path d="M17 12h-4.25V7.75a.75.75 0 0 0-1.5 0V12H7a.75.75 0 0 0 0 1.5h4.25v4.25a.75.75 0 0 0 1.5 0V13.5H17a.75.75 0 0 0 0-1.5z"/>
              </svg>
            </div> */}
            <h2 className="welcome-title">Xin chào! Tôi là AI Medical Assistant</h2>
            <p className="welcome-subtitle">
              Tôi có thể giúp bạn tư vấn về sức khỏe, triệu chứng bệnh và đưa ra lời khuyên y tế. 
              Hãy mô tả triệu chứng hoặc vấn đề sức khỏe mà bạn đang gặp phải.
            </p>
            <div className="welcome-suggestions">
              <h3>Một số câu hỏi gợi ý:</h3>
              <div className="suggestions-grid">
                <button 
                  className="suggestion-item"
                  onClick={() => onSendMessage("Tôi bị đau đầu và chóng mặt, có thể là bệnh gì?")}
                >
                  <span className="suggestion-icon">🤕</span>
                  <span>Triệu chứng đau đầu</span>
                </button>
                <button 
                  className="suggestion-item"
                  onClick={() => onSendMessage("Tôi nên ăn gì để tăng cường hệ miễn dịch?")}
                >
                  <span className="suggestion-icon">🥗</span>
                  <span>Tư vấn dinh dưỡng</span>
                </button>
                <button 
                  className="suggestion-item"
                  onClick={() => onSendMessage("Các biện pháp phòng ngừa COVID-19 hiệu quả?")}
                >
                  <span className="suggestion-icon">😷</span>
                  <span>Phòng ngừa bệnh tật</span>
                </button>
                <button 
                  className="suggestion-item"
                  onClick={() => onSendMessage("Khi nào tôi nên đi khám bác sĩ?")}
                >
                  <span className="suggestion-icon">🏥</span>
                  <span>Tư vấn khám bác sĩ</span>
                </button>
              </div>
            </div>
            {/* <div className="welcome-disclaimer">
              <p>
                ⚠️ <strong>Lưu ý quan trọng:</strong> Thông tin từ AI chỉ mang tính chất tham khảo. 
                Hãy luôn tham khảo ý kiến bác sĩ chuyên khoa để có chẩn đoán và điều trị chính xác.
              </p>
            </div> */}
          </div>
        </div>
      )}

      {/* Messages Area */}
      {messages.length > 0 && (
        <MessageList messages={messages} isLoading={isLoading} />
      )}

      {/* Input Area */}
      <ChatInput
        onSendMessage={onSendMessage}
        isLoading={isLoading}
        disabled={!sessionId}
      />
    </div>
  );
};

export default ChatWindow;