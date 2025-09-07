import { AuthService } from './auth.service';

const BACKEND_API_BASE = 'http://localhost:8080/api';

export interface BackendChatSession {
  id: string;
  sessionType: 'symptom_check' | 'follow_up' | 'general_question' | 'medication_query';
  startedAt: string;
  endedAt?: string;
  totalMessages: number;
  satisfactionRating?: number;
  wasHelpful?: boolean;
}

export interface BackendChatMessage {
  id: number;
  messageOrder: number;
  sender: 'user' | 'ai';
  messageText: string;
  messageType: 'text' | 'symptom_data' | 'diagnosis_result' | 'recommendation';
  aiConfidence?: number;
  processingTimeMs?: number;
  sentimentScore?: number;
  containsUrgencyKeywords: boolean;
  timestamp: string;
}

/**
 * Service để tương tác với Spring Boot backend
 */
export class BackendService {
  
  /**
   * Tạo session chat mới qua Spring Boot
   */
  static async createChatSession(): Promise<BackendChatSession> {
    try {
      const response = await fetch(`${BACKEND_API_BASE}/chat/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...AuthService.getAuthHeaders(),
        },
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message || 'Không thể tạo phiên chat');
      }

      return result.data;
    } catch (error) {
      console.error('Error creating chat session:', error);
      throw error;
    }
  }

  /**
   * Gửi user message qua Spring Boot backend
   */
  static async sendUserMessage(sessionId: string, message: string): Promise<BackendChatMessage> {
    try {
      const response = await fetch(`${BACKEND_API_BASE}/chat/sessions/${sessionId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...AuthService.getAuthHeaders(),
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message || 'Không thể gửi tin nhắn');
      }

      return result.data;
    } catch (error) {
      console.error('Error sending user message:', error);
      throw error;
    }
  }

  /**
   * Lưu AI response qua Spring Boot backend
   */
  static async saveAiResponse(
    sessionId: string, 
    message: string, 
    confidence?: number, 
    processingTime?: number
  ): Promise<BackendChatMessage> {
    try {
      const response = await fetch(`${BACKEND_API_BASE}/chat/sessions/${sessionId}/ai-response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...AuthService.getAuthHeaders(),
        },
        body: JSON.stringify({ 
          message, 
          confidence, 
          processingTime 
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message || 'Không thể lưu phản hồi AI');
      }

      return result.data;
    } catch (error) {
      console.error('Error saving AI response:', error);
      // Không throw để không ảnh hưởng đến UX
      throw error;
    }
  }

  /**
   * Lấy lịch sử chat từ Spring Boot backend
   */
  static async getChatHistory(sessionId: string): Promise<BackendChatMessage[]> {
    try {
      const response = await fetch(`${BACKEND_API_BASE}/chat/sessions/${sessionId}/messages`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...AuthService.getAuthHeaders(),
        },
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message || 'Không thể lấy lịch sử chat');
      }

      return result.data || [];
    } catch (error) {
      console.error('Error fetching chat history:', error);
      return [];
    }
  }

  /**
   * Lấy danh sách sessions của user
   */
  static async getUserSessions(): Promise<BackendChatSession[]> {
    try {
      const response = await fetch(`${BACKEND_API_BASE}/chat/sessions`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...AuthService.getAuthHeaders(),
        },
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message || 'Không thể lấy danh sách phiên chat');
      }

      return result.data || [];
    } catch (error) {
      console.error('Error fetching user sessions:', error);
      return [];
    }
  }

  /**
   * Kết thúc session
   */
  static async endSession(sessionId: string): Promise<void> {
    try {
      const response = await fetch(`${BACKEND_API_BASE}/chat/sessions/${sessionId}/end`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...AuthService.getAuthHeaders(),
        },
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message || 'Không thể kết thúc phiên chat');
      }
    } catch (error) {
      console.error('Error ending session:', error);
      throw error;
    }
  }

  /**
   * Delete chat session
   */
  static async deleteSession(sessionId: string): Promise<void> {
    try {
      const response = await fetch(`${BACKEND_API_BASE}/chat/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...AuthService.getAuthHeaders(),
        },
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message || 'Failed to delete session');
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
      throw error;
    }
  }

  /**
   * Health check backend
   */
  static async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${BACKEND_API_BASE}/chat/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...AuthService.getAuthHeaders(),
        },
        signal: AbortSignal.timeout(5000), // 5s timeout
      });
      
      return response.ok;
    } catch (error) {
      console.warn('Backend health check failed:', error);
      return false;
    }
  }
}
