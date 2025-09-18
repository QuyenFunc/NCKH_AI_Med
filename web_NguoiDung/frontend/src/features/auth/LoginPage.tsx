import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import type { LoginRequest } from '../../types';
import './styles/LoginPage.css';

const LoginPage: React.FC = () => {
  const { login, switchToRegister, error, clearError, isLoading, authMode } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    clearErrors,
  } = useForm<LoginRequest>();

  // Chuyển hướng nếu đã đăng nhập
  useEffect(() => {
    if (authMode === 'authenticated') {
      navigate('/dashboard');
    }
  }, [authMode, navigate]);

  // Xử lý error từ context
  useEffect(() => {
    if (error) {
      toast.error(error);
      clearError();
    }
  }, [error, clearError]);

  const onSubmit = async (data: LoginRequest) => {
    try {
      clearErrors();
      await login(data.email, data.password);
      toast.success('Đăng nhập thành công!');
      navigate('/dashboard');
    } catch (error) {
      // Error đã được xử lý trong AuthContext và hiển thị qua useEffect
      console.error('Login failed:', error);
    }
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
        <form onSubmit={handleSubmit(onSubmit)} className="login-form">
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <div className="input-wrapper">
              <Mail size={20} className="input-icon" />
              <input
                type="email"
                id="email"
                {...register('email', {
                  required: 'Email không được để trống',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Email không đúng định dạng'
                  }
                })}
                className={`form-input ${errors.email ? 'error' : ''}`}
                placeholder=""
              />
            </div>
            {errors.email && (
              <span className="error-message">{errors.email.message}</span>
            )}
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
                {...register('password', {
                  required: 'Mật khẩu không được để trống',
                  minLength: {
                    value: 6,
                    message: 'Mật khẩu phải có ít nhất 6 ký tự'
                  }
                })}
                className={`form-input ${errors.password ? 'error' : ''}`}
                placeholder=""
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
            {errors.password && (
              <span className="error-message">{errors.password.message}</span>
            )}
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
              disabled={isSubmitting || isLoading}
              className="login-btn"
            >
              {(isSubmitting || isLoading) ? (
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