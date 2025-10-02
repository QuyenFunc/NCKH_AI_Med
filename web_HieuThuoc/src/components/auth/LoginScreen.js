import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Lock, User, Package, AlertCircle } from 'lucide-react';
import './LoginScreen.css';

function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    setEmail('pharmacy@ankhang.com');
    setPassword('123456');
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <Package className="login-icon" />
          <h1>Hiệu Thuốc - Portal</h1>
          <p>Hệ thống quản lý hiệu thuốc</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <div className="input-wrapper">
              <User className="input-icon" />
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Nhập email của bạn"
                className="input"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Mật khẩu</label>
            <div className="input-wrapper">
              <Lock className="input-icon" />
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Nhập mật khẩu"
                className="input"
                required
              />
            </div>
          </div>

          {error && (
            <div className="error-message">
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <button type="submit" className="btn btn-primary login-btn" disabled={loading}>
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </button>
        </form>

        <div className="demo-section">
          <p>Tài khoản demo (Hiệu thuốc An Khang):</p>
          <div className="demo-info">
            <p className="demo-credentials">
              📧 Email: <strong>pharmacy@ankhang.com</strong><br/>
              🔑 Password: <strong>123456</strong>
            </p>
          </div>
          <div className="demo-buttons">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleDemoLogin}
            >
              Điền thông tin Demo
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginScreen;

