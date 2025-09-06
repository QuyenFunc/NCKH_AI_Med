import React from 'react';
import { AlertCircle, Wifi, WifiOff } from 'lucide-react';
import { useChat } from '../contexts';
import { useOnlineStatus } from '../hooks';

export const GlobalNotifications: React.FC = () => {
  const { error, sessionId, clearError, startNewSession } = useChat();
  const isOnline = useOnlineStatus();

  return (
    <>
      {/* Offline Warning */}
      {!isOnline && (
        <div className="offline-warning">
          <div className="offline-content">
            <WifiOff size={16} />
            <span>Không có kết nối internet</span>
          </div>
        </div>
      )}

      {/* Connection Status */}
      {/* {isOnline && sessionId && (
        <div className="connection-status">
          <div className="connection-content">
            <Wifi size={14} />
            <span>Đã kết nối</span>
          </div>
        </div>
      )} */}

      {/* Error Toast */}
      {error && (
        <div className="error-toast">
          <div className="error-content">
            <div className="error-header">
              <AlertCircle size={18} />
              <div className="error-text">
                <p className="error-title">Có lỗi xảy ra</p>
                <p className="error-message">{error}</p>
                <div className="error-actions">
                  <button onClick={clearError} className="error-btn">
                    Đóng
                  </button>
                  <button onClick={startNewSession} className="error-btn">
                    Thử lại
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
