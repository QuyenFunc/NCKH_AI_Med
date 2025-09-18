import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  MessageSquare, 
  Plus, 
  Menu, 
  History, 
  Settings, 
  User, 
  LogOut,
  Sparkles,
  MoreHorizontal
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useChat } from '../../contexts/ChatContext';
import { useSession } from '../../contexts/SessionContext';
import { BackendService, type BackendChatSession } from '../../services/backend.service';
import { ContextMenu } from '../chat/ContextMenu';
import { ROUTES } from '../../constants';
import { logger } from '../../constants/config';
import './styles/MainLayout.css';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const { sessionId: urlSessionId } = useParams<{ sessionId?: string }>();
  const { logout } = useAuth();
  const { startNewSession, loadExistingSession, sessionId } = useChat();
  const { onSessionCreated } = useSession();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [chatSessions, setChatSessions] = useState<BackendChatSession[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [contextMenu, setContextMenu] = useState<{
    isOpen: boolean;
    sessionId: string | null;
    position: { x: number; y: number };
  }>({
    isOpen: false,
    sessionId: null,
    position: { x: 0, y: 0 }
  });

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleSettingsClick = () => {
    navigate(ROUTES.SETTINGS);
  };

  // ✅ Load real chat sessions from backend
  const loadChatSessions = async () => {
    try {
      setLoadingSessions(true);
      logger.info('Loading user chat sessions');
      const sessions = await BackendService.getUserSessions();
      setChatSessions(sessions);
      logger.info(`Loaded ${sessions.length} chat sessions`);
    } catch (error) {
      logger.error('Failed to load chat sessions:', error);
      // Don't show error to user, just keep empty list
    } finally {
      setLoadingSessions(false);
    }
  };

  // ✅ Load sessions when component mounts
  useEffect(() => {
    loadChatSessions();
  }, []);

  // ✅ Register callback for session creation
  useEffect(() => {
    onSessionCreated(() => {
      logger.info('New session created, reloading chat sessions');
      loadChatSessions();
    });
  }, [onSessionCreated]);

  // ✅ Load session from URL params or auto-load latest
  useEffect(() => {
    if (urlSessionId && urlSessionId !== sessionId) {
      logger.info('Loading session from URL:', urlSessionId);
      loadExistingSession(urlSessionId);
    } else if (!urlSessionId && chatSessions.length > 0 && !sessionId) {
      // ✅ Auto-navigate to latest session when no sessionId in URL
      const latestSession = chatSessions[0]; // Sessions are ordered by startedAt desc
      logger.info('Auto-navigating to latest session:', latestSession.id);
      navigate(`/chat/${latestSession.id}`, { replace: true }); // Replace current history entry
    }
  }, [urlSessionId, sessionId, loadExistingSession, chatSessions, navigate]);


  // ✅ Handle session click
  const handleSessionClick = async (session: BackendChatSession) => {
    if (session.id !== sessionId) {
      logger.info('Switching to session:', session.id);
      // Only navigate - let URL params handle the loading
      navigate(`/chat/${session.id}`);
    }
  };

  // ✅ Handle new chat
  const handleNewChat = async () => {
    try {
      const newSessionId = await startNewSession(true); // ✅ Force create new session
      // Navigate to new session URL
      if (newSessionId) {
        navigate(`/chat/${newSessionId}`);
        // ✅ Chat sessions will be reloaded automatically via callback
      } else {
        navigate('/chat');
      }
    } catch (error) {
      logger.error('Failed to start new session:', error);
    }
  };

  // ✅ Handle context menu
  const handleContextMenu = (event: React.MouseEvent, sessionId: string) => {
    event.preventDefault();
    event.stopPropagation();
    
    setContextMenu({
      isOpen: true,
      sessionId,
      position: { x: event.clientX, y: event.clientY }
    });
  };

  const closeContextMenu = () => {
    setContextMenu({
      isOpen: false,
      sessionId: null,
      position: { x: 0, y: 0 }
    });
  };

  const handleDeleteSession = async () => {
    if (!contextMenu.sessionId) return;
    
    try {
      await BackendService.deleteSession(contextMenu.sessionId);
      logger.info('Session deleted:', contextMenu.sessionId);
      
      // Reload chat sessions
      await loadChatSessions();
      
      // If deleted session is current session, navigate to chat home
      if (contextMenu.sessionId === sessionId) {
        navigate('/chat');
      }
      
      closeContextMenu();
    } catch (error) {
      logger.error('Failed to delete session:', error);
      // TODO: Show error toast
    }
  };

  // ✅ Format session time
  const formatSessionTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffMs / (1000 * 60));

    if (diffMinutes < 60) {
      return `${diffMinutes} phút trước`;
    } else if (diffHours < 24) {
      return `${diffHours} giờ trước`;
    } else if (diffDays === 1) {
      return 'Hôm qua';
    } else if (diffDays < 7) {
      return `${diffDays} ngày trước`;
    } else {
      return date.toLocaleDateString('vi-VN');
    }
  };

  // ✅ Generate session title based on type
  const getSessionTitle = (session: BackendChatSession): string => {
    switch (session.sessionType) {
      case 'symptom_check':
        return 'Kiểm tra triệu chứng';
      case 'follow_up':
        return 'Tái khám theo dõi';
      case 'medication_query':
        return 'Hỏi về thuốc';
      case 'general_question':
      default:
        return 'Tư vấn sức khỏe';
    }
  };

  return (
    <div className="main-layout">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <button onClick={handleNewChat} className="new-chat-btn">
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
            {loadingSessions ? (
              <div className="loading-sessions">
                <span>Đang tải lịch sử...</span>
              </div>
            ) : chatSessions.length > 0 ? (
              chatSessions.map((session) => (
                <div 
                  key={session.id} 
                  className={`history-item ${session.id === sessionId ? 'active' : ''}`}
                  onClick={() => handleSessionClick(session)}
                >
                  <div className="history-content">
                    <MessageSquare size={16} />
                    <div className="history-text">
                      <p className="history-title">{getSessionTitle(session)}</p>
                      <p className="history-time">{formatSessionTime(session.startedAt)}</p>
                      <p className="history-meta">{session.totalMessages} tin nhắn</p>
                    </div>
                  </div>
                  <button
                    className="context-menu-trigger"
                    onClick={(e) => handleContextMenu(e, session.id)}
                    onMouseDown={(e) => e.stopPropagation()}
                  >
                    <MoreHorizontal size={16} />
                  </button>
                </div>
              ))
            ) : (
              <div className="no-sessions">
                <span>Chưa có lịch sử chat</span>
              </div>
            )}
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

      {/* Context Menu */}
      <ContextMenu
        isOpen={contextMenu.isOpen}
        onClose={closeContextMenu}
        onDelete={handleDeleteSession}
        position={contextMenu.position}
      />
    </div>
  );
};

export default MainLayout;
