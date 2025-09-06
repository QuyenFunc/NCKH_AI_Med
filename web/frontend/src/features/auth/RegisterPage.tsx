import React, { useState } from 'react';
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
import './styles/RegisterPage.css';

const RegisterPage: React.FC = () => {
  const { register, switchToLogin } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [agreeToTerms, setAgreeToTerms] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const getPasswordStrength = (password: string) => {
    if (password.length < 6) return 'weak';
    if (password.length < 10) return 'medium';
    return 'strong';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agreeToTerms) {
      alert('Vui lòng đồng ý với điều khoản dịch vụ');
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      alert('Mật khẩu xác nhận không khớp');
      return;
    }
    
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      register(formData.name, formData.email, formData.password);
      setIsLoading(false);
    }, 1500);
  };

  const passwordStrength = getPasswordStrength(formData.password);

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
        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <label htmlFor="name" className="form-label">
              Họ và tên
            </label>
            <div className="input-wrapper">
              <User size={20} className="input-icon" />
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Nhập họ và tên của bạn"
                required
              />
            </div>
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
                name="email"
                value={formData.email}
                onChange={handleInputChange}
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
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="form-input"
                placeholder="••••••••••"
                required
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
            {formData.password && (
              <div className="password-strength">
                <div className="strength-label">
                  Độ mạnh: {passwordStrength === 'weak' ? 'Yếu' : passwordStrength === 'medium' ? 'Trung bình' : 'Mạnh'}
                </div>
                <div className="strength-bar">
                  <div className={`strength-fill ${passwordStrength}`}></div>
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
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Nhập lại mật khẩu"
                required
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
              disabled={isLoading || !agreeToTerms}
              className="register-btn"
            >
              {isLoading ? (
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