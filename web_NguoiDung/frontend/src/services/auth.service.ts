import type { LoginRequest, RegisterRequest, AuthResponse, ApiResponse, UserInfo } from '../types';
import { API_CONFIG } from '../constants/api';

/**
 * Auth Service cho backend Spring Boot
 * Sử dụng fetch API để giao tiếp với backend
 */
export class AuthService {
  private static readonly TOKEN_KEY = 'nckh_auth_token';
  private static readonly USER_KEY = 'nckh_user_info';

  /**
   * Đăng nhập
   */
  static async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: Đăng nhập thất bại`);
      }

      const result: ApiResponse<AuthResponse> = await response.json();
      
      if (!result.success || !result.data) {
        throw new Error(result.message || 'Đăng nhập thất bại');
      }

      // Lưu token và thông tin user
      this.saveToken(result.data.accessToken);
      this.saveUserInfo(result.data.user);

      return result.data;
    } catch (error) {
      console.error('Login error:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Không thể kết nối với server');
    }
  }

  /**
   * Đăng ký
   */
  static async register(userData: RegisterRequest): Promise<AuthResponse> {
    try {
      // Validate confirm password
      if (userData.password !== userData.confirmPassword) {
        throw new Error('Mật khẩu xác nhận không khớp');
      }

      const response = await fetch(`${API_CONFIG.BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userData.email,
          password: userData.password,
          confirmPassword: userData.confirmPassword,
          name: userData.name,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: Đăng ký thất bại`);
      }

      const result: ApiResponse<AuthResponse> = await response.json();
      
      if (!result.success || !result.data) {
        throw new Error(result.message || 'Đăng ký thất bại');
      }

      // Lưu token và thông tin user
      this.saveToken(result.data.accessToken);
      this.saveUserInfo(result.data.user);

      return result.data;
    } catch (error) {
      console.error('Register error:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Không thể kết nối với server');
    }
  }

  /**
   * Đăng xuất
   */
  static async logout(): Promise<void> {
    try {
      // Gọi API logout (optional với JWT stateless)
      const token = this.getToken();
      if (token) {
        await fetch(`${API_CONFIG.BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }).catch(() => {
          // Ignore errors for logout API
        });
      }
    } finally {
      // Clear local storage
      this.clearAuth();
    }
  }

  /**
   * Lấy thông tin user hiện tại
   */
  static async getCurrentUser(): Promise<UserInfo> {
    const token = this.getToken();
    if (!token) {
      throw new Error('Không có token xác thực');
    }

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          this.clearAuth();
          throw new Error('Token đã hết hạn');
        }
        throw new Error(`HTTP ${response.status}: Không thể lấy thông tin user`);
      }

      const result: ApiResponse<UserInfo> = await response.json();
      
      if (!result.success || !result.data) {
        throw new Error(result.message || 'Không thể lấy thông tin user');
      }

      // Cập nhật thông tin user trong localStorage
      this.saveUserInfo(result.data);

      return result.data;
    } catch (error) {
      console.error('Get current user error:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Không thể kết nối với server');
    }
  }

  /**
   * Lưu token vào localStorage
   */
  static saveToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  /**
   * Lấy token từ localStorage
   */
  static getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Lưu thông tin user vào localStorage
   */
  static saveUserInfo(user: UserInfo): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  /**
   * Lấy thông tin user từ localStorage
   */
  static getUserInfo(): UserInfo | null {
    try {
      const userStr = localStorage.getItem(this.USER_KEY);
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  }

  /**
   * Kiểm tra user đã đăng nhập chưa
   */
  static isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /**
   * Xóa tất cả thông tin xác thực
   */
  static clearAuth(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  /**
   * Tạo Authorization header
   */
  static getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
}
