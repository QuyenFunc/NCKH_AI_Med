import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { 
  User, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight,
  UserPlus
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import type { RegisterRequest } from '../../types';
import './styles/RegisterPage.css';

const RegisterPage: React.FC = () => {
  const { register: registerUser, switchToLogin, error, clearError, isLoading, authMode } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeToTerms, setAgreeToTerms] = useState(false);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    setError,
    clearErrors,
  } = useForm<RegisterRequest>();

  const watchedPassword = watch('password', '');

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

  const getPasswordStrength = (password: string) => {
    if (password.length < 6) return 'weak';
    if (password.length < 10) return 'medium';
    return 'strong';
  };

  const onSubmit = async (data: RegisterRequest) => {
    try {
      if (!agreeToTerms) {
        toast.error('Vui lòng đồng ý với điều khoản dịch vụ');
        return;
      }

      clearErrors();
      await registerUser(data.name || '', data.email, data.password, data.confirmPassword);
      toast.success('Đăng ký thành công!');
      navigate('/dashboard');
    } catch (error) {
      // Error đã được xử lý trong AuthContext và hiển thị qua useEffect
      console.error('Register failed:', error);
    }
  };


  return (
    <div className="register-page">
      <div className="register-container">
        {/* Header */}
        <div className="form-header">
          <div className="app-logo">
            <UserPlus size={28} />
          </div>
          <h1 className="form-title">Tạo tài khoản</h1>
          <p className="form-subtitle">
            Tham gia cùng chúng tôi để trải nghiệm dịch vụ tốt nhất
          </p>
        </div>

        {/* Register Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="register-form">
          <div className="form-group">
            <label htmlFor="name" className="form-label">
              Họ và tên
            </label>
            <div className="input-wrapper">
              <User size={20} className="input-icon" />
              <input
                type="text"
                id="name"
                {...register('name', {
                  maxLength: {
                    value: 255,
                    message: 'Tên không được quá 255 ký tự'
                  }
                })}
                className={`form-input ${errors.name ? 'error' : ''}`}
                placeholder="Nhập họ và tên của bạn"
              />
            </div>
            {errors.name && (
              <span className="error-message">{errors.name.message}</span>
            )}
          </div>

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
                placeholder="••••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="password-toggle"
                aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiển thị mật khẩu'}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            {errors.password && (
              <span className="error-message">{errors.password.message}</span>
            )}
            {watchedPassword && (
              <div className="password-strength">
                <div className="strength-label">
                  Độ mạnh: {getPasswordStrength(watchedPassword) === 'weak' ? 'Yếu' : getPasswordStrength(watchedPassword) === 'medium' ? 'Trung bình' : 'Mạnh'}
                </div>
                <div className="strength-bar">
                  <div className={`strength-fill ${getPasswordStrength(watchedPassword)}`}></div>
                </div>
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword" className="form-label">
              Xác nhận mật khẩu
            </label>
            <div className="input-wrapper">
              <Lock size={20} className="input-icon" />
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                id="confirmPassword"
                {...register('confirmPassword', {
                  required: 'Xác nhận mật khẩu không được để trống',
                  validate: (value) => 
                    value === watchedPassword || 'Mật khẩu xác nhận không khớp'
                })}
                className={`form-input ${errors.confirmPassword ? 'error' : ''}`}
                placeholder="Nhập lại mật khẩu"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="password-toggle"
                aria-label={showConfirmPassword ? 'Ẩn mật khẩu' : 'Hiển thị mật khẩu'}
              >
                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            {errors.confirmPassword && (
              <span className="error-message">{errors.confirmPassword.message}</span>
            )}
          </div>

          <div className="terms-agreement">
            <input
              type="checkbox"
              id="terms"
              checked={agreeToTerms}
              onChange={(e) => setAgreeToTerms(e.target.checked)}
              className="terms-checkbox"
            />
            <label htmlFor="terms" className="terms-text">
              Tôi đồng ý với{' '}
              <a href="#" className="terms-link">
                Điều khoản dịch vụ
              </a>{' '}
              và{' '}
              <a href="#" className="terms-link">
                Chính sách bảo mật
              </a>
            </label>
          </div>

          <div className="form-actions">
            <button
              type="submit"
              disabled={isSubmitting || isLoading || !agreeToTerms}
              className="register-btn"
            >
              {(isSubmitting || isLoading) ? (
                <>
                  <div className="loading-spinner" />
                  Đang tạo tài khoản...
                </>
              ) : (
                <>
                  Tạo tài khoản
                  <ArrowRight size={20} />
                </>
              )}
            </button>
          </div>
        </form>

        {/* Switch to Login */}
        <div className="switch-mode">
          <p className="switch-text">Đã có tài khoản?</p>
          <button
            type="button"
            onClick={switchToLogin}
            className="switch-btn"
          >
            Đăng nhập ngay
          </button>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;