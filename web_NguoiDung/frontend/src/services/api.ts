import type { ProfileFormData } from '../types';
import { APP_CONFIG, isMockMode, logger } from '../constants/config';

export class ApiService {
  // Session Management
  static async createSession(): Promise<string> {
    logger.info('Creating session...', { mockMode: isMockMode() });
    
    if (isMockMode()) {
      // Mock mode: chỉ generate session ID
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      await new Promise(resolve => setTimeout(resolve, 200));
      logger.info('Mock session created:', sessionId);
      return sessionId;
    }
    
    // Backend mode: kết nối thật với backend
    try {
      const response = await fetch(`${APP_CONFIG.API_BASE_URL}/chat/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(APP_CONFIG.API_TIMEOUT),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      logger.info('Backend session created:', data.sessionId);
      return data.sessionId;
    } catch (error) {
      logger.error('Error creating session:', error);
      // Fallback: tạo temporary session để user vẫn có thể thấy UI
      const fallbackSessionId = `temp_session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      logger.warn('Using fallback session:', fallbackSessionId);
      return fallbackSessionId;
    }
  }

  // Chat Streaming
  static async* streamChat(
    sessionId: string,
    query: string
  ): AsyncGenerator<string, void, unknown> {
    logger.info('Streaming chat...', { sessionId, query, mockMode: isMockMode() });
    
    if (isMockMode()) {
      // Mock mode: generate mock responses
      const responses = this.generateMockResponse(query);
      for (const chunk of responses) {
        await new Promise(resolve => setTimeout(resolve, 100));
        yield chunk;
      }
      return;
    }

    // Backend mode: stream từ backend thật
    try {
      const response = await fetch(`${APP_CONFIG.API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sessionId, query }),
        signal: AbortSignal.timeout(APP_CONFIG.API_TIMEOUT),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = new TextDecoder().decode(value);
        yield chunk;
      }
    } catch (error) {
      logger.error('Error in stream chat:', error);
      // Nếu backend không có, fallback về mock response
      logger.warn('Backend not available, falling back to error message');
      yield "⚠️ **Kết nối với AI đang gặp sự cố**\n\n";
      yield "Hiện tại không thể kết nối với server backend. ";
      yield "Vui lòng:\n\n";
      yield "1. Kiểm tra backend đang chạy tại `http://localhost:8080`\n";
      yield "2. Hoặc bật lại Mock Mode trong settings\n";
      yield "3. Refresh trang và thử lại\n\n";
      yield "**Lỗi chi tiết:** " + (error instanceof Error ? error.message : 'Unknown error');
    }
  }

  // Generate mock responses cho mock mode
  private static generateMockResponse(query: string): string[] {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('đau đầu') || lowerQuery.includes('đau') || lowerQuery.includes('nhức')) {
      return [
        "Tôi hiểu bạn đang gặp vấn đề về đau đầu. ",
        "Để có thể hỗ trợ bạn tốt hơn, tôi cần biết thêm một số thông tin:\n\n",
        "**Các câu hỏi quan trọng:**\n",
        "1. Đau đầu xuất hiện từ bao lâu?\n",
        "2. Mức độ đau từ 1-10 (10 là đau nhất)?\n",
        "3. Đau ở vị trí nào (trán, thái dương, đỉnh đầu)?\n",
        "4. Có kèm theo triệu chứng khác không?\n\n",
        "⚠️ **Lưu ý:** Đây chỉ là thông tin tham khảo. Nếu đau đầu kéo dài hoặc nghiêm trọng, hãy tham khảo ý kiến bác sĩ."
      ];
    }
    
    if (lowerQuery.includes('sốt') || lowerQuery.includes('nóng')) {
      return [
        "Bạn đang có triệu chứng sốt. Đây là dấu hiệu cơ thể đang chống lại nhiễm trùng.\n\n",
        "**Thông tin cần thiết:**\n",
        "1. Nhiệt độ cơ thể hiện tại?\n",
        "2. Sốt bao lâu rồi?\n",
        "3. Có triệu chứng kèm theo như ho, đau họng?\n\n",
        "**Khuyến nghị:**\n",
        "- Uống nhiều nước\n",
        "- Nghỉ ngơi đầy đủ\n",
        "- Nếu sốt >38.5°C hoặc kéo dài >3 ngày, cần đến bác sĩ"
      ];
    }
    
    if (lowerQuery.includes('ho') || lowerQuery.includes('cảm')) {
      return [
        "Triệu chứng ho có thể do nhiều nguyên nhân khác nhau.\n\n",
        "**Các câu hỏi chẩn đoán:**\n",
        "1. Ho khan hay có đờm?\n",
        "2. Ho bao lâu rồi?\n",
        "3. Có kèm sốt, đau họng không?\n",
        "4. Có tiếp xúc với người bệnh?\n\n",
        "**Chăm sóc ban đầu:**\n",
        "- Uống nước ấm, mật ong\n",
        "- Tránh khói thuốc\n",
        "- Nghỉ ngơi đầy đủ"
      ];
    }
    
    // Default response
    return [
      "Cảm ơn bạn đã chia sẻ triệu chứng. ",
      "Để có thể hỗ trợ bạn tốt nhất, tôi cần thu thập thêm thông tin:\n\n",
      "**Thông tin cần thiết:**\n",
      "1. Triệu chứng xuất hiện từ bao lâu?\n",
      "2. Mức độ nghiêm trọng (1-10)?\n",
      "3. Có triệu chứng kèm theo không?\n",
      "4. Bạn có tiền sử bệnh gì không?\n",
      "5. Đang dùng thuốc gì không?\n\n",
      "⚠️ **Quan trọng:** Đây chỉ là thông tin tham khảo. Với triệu chứng nghiêm trọng hoặc kéo dài, hãy tham khảo ý kiến bác sĩ chuyên khoa."
    ];
  }

  // Send Message
  static async sendMessage(sessionId: string, query: string): Promise<string> {
    let fullResponse = '';
    
    try {
      for await (const chunk of this.streamChat(sessionId, query)) {
        fullResponse += chunk;
      }
      return fullResponse;
    } catch (error) {
      logger.error('Error sending message:', error);
      throw new ApiError('Không thể gửi tin nhắn');
    }
  }

  // Profile Management
  static async saveProfile(data: ProfileFormData): Promise<{ success: boolean }> {
    logger.info('Saving profile...', { mockMode: isMockMode() });
    
    if (isMockMode()) {
      // Mock mode
      await new Promise(resolve => setTimeout(resolve, APP_CONFIG.MOCK_RESPONSE_DELAY));
      const success = Math.random() > (1 - APP_CONFIG.MOCK_SUCCESS_RATE);
      logger.info('Mock profile save result:', success);
      return { success };
    }

    // Backend mode
    try {
      const response = await fetch(`${APP_CONFIG.API_BASE_URL}/users/profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // 'Authorization': `Bearer ${getAuthToken()}`, // Thêm auth header khi cần
        },
        body: JSON.stringify(data),
        signal: AbortSignal.timeout(APP_CONFIG.API_TIMEOUT),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      logger.info('Backend profile save result:', result);
      return result;
    } catch (error) {
      logger.error('Save profile error:', error);
      throw new ApiError('Có lỗi xảy ra khi lưu hồ sơ');
    }
  }

  // Authentication
  static async login(email: string, password: string) {
    logger.info('Login attempt...', { email, mockMode: isMockMode() });
    
    if (isMockMode()) {
      // Mock mode
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (!email || !password) {
        throw new ApiError('Email và mật khẩu không được để trống');
      }
      
      return {
        success: true,
        user: {
          id: '1',
          name: 'Người dùng Demo',
          email: email
        },
        token: 'mock_jwt_token_' + Date.now()
      };
    }

    // Backend mode
    try {
      const response = await fetch(`${APP_CONFIG.API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
        signal: AbortSignal.timeout(APP_CONFIG.API_TIMEOUT),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      logger.info('Backend login result:', result);
      return result;
    } catch (error) {
      logger.error('Login error:', error);
      throw new ApiError('Đăng nhập thất bại');
    }
  }

  static async register(email: string, password: string, name: string) {
    logger.info('Register attempt...', { email, name, mockMode: isMockMode() });
    
    if (isMockMode()) {
      // Mock mode
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (!email || !password || !name) {
        throw new ApiError('Vui lòng điền đầy đủ thông tin');
      }
      
      return {
        success: true,
        user: {
          id: '1',
          name: name,
          email: email
        },
        token: 'mock_jwt_token_' + Date.now()
      };
    }

    // Backend mode
    try {
      const response = await fetch(`${APP_CONFIG.API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name }),
        signal: AbortSignal.timeout(APP_CONFIG.API_TIMEOUT),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      logger.info('Backend register result:', result);
      return result;
    } catch (error) {
      logger.error('Register error:', error);
      throw new ApiError('Đăng ký thất bại');
    }
  }

  static async getCurrentUser(token: string) {
    logger.info('Getting current user...', { mockMode: isMockMode() });
    
    if (isMockMode()) {
      // Mock mode
      await new Promise(resolve => setTimeout(resolve, 500));
      
      return {
        id: '1',
        name: 'Người dùng Demo',
        email: 'user@demo.com',
        profile: {
          hasCompletedSetup: true
        }
      };
    }

    // Backend mode
    try {
      const response = await fetch(`${APP_CONFIG.API_BASE_URL}/users/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(APP_CONFIG.API_TIMEOUT),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      logger.info('Backend get user result:', result);
      return result;
    } catch (error) {
      logger.error('Get user error:', error);
      throw new ApiError('Không thể lấy thông tin người dùng');
    }
  }

  // Health Check
  static async healthCheck(): Promise<boolean> {
    if (isMockMode()) {
      // Mock mode: always healthy
      logger.info('Mock health check: healthy');
      return true;
    }

    // Backend mode: check thật
    try {
      const response = await fetch(`${APP_CONFIG.API_BASE_URL}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000), // 5s timeout cho health check
      });
      
      const isHealthy = response.status === 200;
      logger.info('Backend health check:', isHealthy);
      return isHealthy;
    } catch (error) {
      logger.error('Health check failed:', error);
      return false;
    }
  }
}

export class ApiError extends Error {
  public code?: string;
  public details?: any;
  
  constructor(message: string, code?: string, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
  }
}