import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  User, 
  Shield, 
  Bell, 
  Palette,
  Info,
  HelpCircle 
} from 'lucide-react';
import { ThemeToggle } from '../../components/ui/ThemeToggle';
import { ROUTES } from '../../constants';
import './styles/SettingsPage.css';

export const SettingsPage: React.FC = () => {
  const navigate = useNavigate();

  const handleBackClick = () => {
    navigate(ROUTES.DASHBOARD);
  };

  return (
    <div className="settings-page">
      {/* Header */}
      <div className="settings-header">
        <button onClick={handleBackClick} className="back-button">
          <ArrowLeft size={20} />
        </button>
        <h1 className="settings-title">Cài đặt</h1>
      </div>

      {/* Settings Content */}
      <div className="settings-content">
        <div className="settings-container">
          
          {/* Appearance Section */}
          <div className="settings-section">
            <div className="section-header">
              <Palette size={20} className="section-icon" />
              <h2 className="section-title">Giao diện</h2>
            </div>
            
            <div className="settings-group">
              <div className="setting-item">
                <div className="setting-info">
                  <h3 className="setting-title">Chế độ tối</h3>
                  <p className="setting-description">
                    Bật chế độ tối để giảm mỏi mắt khi sử dụng trong môi trường thiếu ánh sáng
                  </p>
                </div>
                <div className="setting-control">
                  <ThemeToggle showLabel={false} size="md" />
                </div>
              </div>
            </div>
          </div>

          {/* Account Section */}
          <div className="settings-section">
            <div className="section-header">
              <User size={20} className="section-icon" />
              <h2 className="section-title">Tài khoản</h2>
            </div>
            
            <div className="settings-group">
              <button className="setting-item clickable">
                <div className="setting-info">
                  <h3 className="setting-title">Hồ sơ cá nhân</h3>
                  <p className="setting-description">Quản lý thông tin cá nhân và hồ sơ y tế</p>
                </div>
                <ArrowLeft size={16} className="setting-arrow" />
              </button>
              
              <button className="setting-item clickable">
                <div className="setting-info">
                  <h3 className="setting-title">Thay đổi mật khẩu</h3>
                  <p className="setting-description">Cập nhật mật khẩu đăng nhập của bạn</p>
                </div>
                <ArrowLeft size={16} className="setting-arrow" />
              </button>
            </div>
          </div>

          {/* Privacy & Security Section */}
          <div className="settings-section">
            <div className="section-header">
              <Shield size={20} className="section-icon" />
              <h2 className="section-title">Bảo mật & Riêng tư</h2>
            </div>
            
            <div className="settings-group">
              <button className="setting-item clickable">
                <div className="setting-info">
                  <h3 className="setting-title">Quyền riêng tư dữ liệu</h3>
                  <p className="setting-description">Quản lý cách dữ liệu của bạn được sử dụng</p>
                </div>
                <ArrowLeft size={16} className="setting-arrow" />
              </button>
              
              <button className="setting-item clickable">
                <div className="setting-info">
                  <h3 className="setting-title">Lịch sử trò chuyện</h3>
                  <p className="setting-description">Xem và quản lý lịch sử tương tác với AI</p>
                </div>
                <ArrowLeft size={16} className="setting-arrow" />
              </button>
            </div>
          </div>

          {/* Notifications Section */}
          <div className="settings-section">
            <div className="section-header">
              <Bell size={20} className="section-icon" />
              <h2 className="section-title">Thông báo</h2>
            </div>
            
            <div className="settings-group">
              <div className="setting-item">
                <div className="setting-info">
                  <h3 className="setting-title">Thông báo nhắc nhở</h3>
                  <p className="setting-description">Nhận thông báo về lịch uống thuốc và khám bệnh</p>
                </div>
                <div className="setting-control">
                  <ThemeToggle showLabel={false} size="sm" />
                </div>
              </div>
              
              <div className="setting-item">
                <div className="setting-info">
                  <h3 className="setting-title">Thông báo hệ thống</h3>
                  <p className="setting-description">Nhận thông báo về cập nhật ứng dụng và tính năng mới</p>
                </div>
                <div className="setting-control">
                  <ThemeToggle showLabel={false} size="sm" />
                </div>
              </div>
            </div>
          </div>

          {/* Help & About Section */}
          <div className="settings-section">
            <div className="section-header">
              <Info size={20} className="section-icon" />
              <h2 className="section-title">Hỗ trợ & Thông tin</h2>
            </div>
            
            <div className="settings-group">
              <button className="setting-item clickable">
                <div className="setting-info">
                  <h3 className="setting-title">Trung tâm trợ giúp</h3>
                  <p className="setting-description">Tìm hiểu cách sử dụng ứng dụng hiệu quả</p>
                </div>
                <ArrowLeft size={16} className="setting-arrow" />
              </button>
              
              <button className="setting-item clickable">
                <div className="setting-info">
                  <h3 className="setting-title">Liên hệ hỗ trợ</h3>
                  <p className="setting-description">Báo cáo lỗi hoặc gửi phản hồi</p>
                </div>
                <ArrowLeft size={16} className="setting-arrow" />
              </button>
              
              <button className="setting-item clickable">
                <div className="setting-info">
                  <h3 className="setting-title">Về ứng dụng</h3>
                  <p className="setting-description">Phiên bản và thông tin pháp lý</p>
                </div>
                <ArrowLeft size={16} className="setting-arrow" />
              </button>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
};
