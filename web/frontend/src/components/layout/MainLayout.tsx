import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  MessageSquare, 
  Plus, 
  Menu, 
  History, 
  Settings, 
  User, 
  LogOut,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useChat } from '../../contexts/ChatContext';
import { ROUTES } from '../../constants';
import './styles/MainLayout.css';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { startNewSession } = useChat();
  const [sidebarOpen, setSidebarOpen] = useState(true);


  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleSettingsClick = () => {
    navigate(ROUTES.SETTINGS);
  };

  // Mock chat history
  const chatHistory = [
    { id: '1', title: 'Triệu chứng đau đầu', time: '2 giờ trước' },
    { id: '2', title: 'Tư vấn về chế độ ăn uống', time: 'Hôm qua' },
    { id: '3', title: 'Kiểm tra sức khỏe định kỳ', time: '2 ngày trước' },
    { id: '4', title: 'Hỏi về vaccine COVID-19', time: '1 tuần trước' },
  ];

  return (
    <div className="main-layout">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <button onClick={startNewSession} className="new-chat-btn">
            <Plus size={20} />
            <span>Cuộc trò chuyện mới</span>
          </button>
        </div>

        {/* Chat History */}
        <div className="chat-history">
          <div className="history-header">
            <History size={16} />
            <span>Lịch sử trò chuyện</span>
          </div>
          <div className="history-list">
            {chatHistory.map((chat) => (
              <button key={chat.id} className="history-item">
                <div className="history-content">
                  <MessageSquare size={16} />
                  <div className="history-text">
                    <p className="history-title">{chat.title}</p>
                    <p className="history-time">{chat.time}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* User Menu */}
        <div className="user-menu">
          <button className="menu-item">
            <User size={18} />
            <span>Hồ sơ</span>
          </button>
          <button onClick={handleSettingsClick} className="menu-item">
            <Settings size={18} />
            <span>Cài đặt</span>
          </button>
          <button onClick={logout} className="menu-item logout">
            <LogOut size={18} />
            <span>Đăng xuất</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <header className="main-header">
          <div className="header-left">
            <button onClick={toggleSidebar} className="menu-toggle">
              <Menu size={20} />
            </button>
            <div className="header-title">
              <div className="app-icon">
                <Sparkles size={20} />
              </div>
              <div>
                <h1>Medical AI Assistant</h1>
              </div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="content-area">
          {children}
        </div>
      </div>
    </div>
  );
};

export default MainLayout;
