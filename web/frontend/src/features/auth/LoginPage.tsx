import React, { useState } from 'react';
import { 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import './styles/LoginPage.css';

const LoginPage: React.FC = () => {
  const { login, switchToRegister } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      login(email, password);
      setIsLoading(false);
    }, 1500);
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="login-page">
      <div className="login-container">
        {/* Header */}
        <div className="form-header">
          <div className="app-logo">
            <Sparkles size={28} />
          </div>
          <h1 className="form-title">Đăng nhập</h1>
          <p className="form-subtitle">
            Chào mừng bạn trở lại! Hãy đăng nhập để tiếp tục.
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <div className="input-wrapper">
              <Mail size={20} className="input-icon" />
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="form-input"
                placeholder=""
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Mật khẩu
            </label>
            <div className="input-wrapper">
              <Lock size={20} className="input-icon" />
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="form-input"
                placeholder=""
                required
              />
              <button
                type="button"
                onClick={togglePasswordVisibility}
                className="password-toggle"
                aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiển thị mật khẩu'}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <div className="form-options">
            <label className="remember-me">
              <input
                type="checkbox"
                className="remember-checkbox"
              />
              <span className="remember-label">Ghi nhớ đăng nhập</span>
            </label>
            <a href="#" className="forgot-link">
              Quên mật khẩu?
            </a>
          </div>

          <div className="form-actions">
            <button
              type="submit"
              disabled={isLoading}
              className="login-btn"
            >
              {isLoading ? (
                <>
                  <div className="loading-spinner" />
                  Đang đăng nhập...
                </>
              ) : (
                <>
                  Đăng nhập
                  <ArrowRight size={20} />
                </>
              )}
            </button>
          </div>
        </form>

        {/* Switch to Register */}
        <div className="switch-mode">
          <p className="switch-text">Chưa có tài khoản?</p>
          <button
            type="button"
            onClick={switchToRegister}
            className="switch-btn"
          >
            Đăng ký ngay
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;