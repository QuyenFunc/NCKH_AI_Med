import { useState, useCallback, useEffect, useRef } from 'react';
import type { Message } from '../types';
import { ApiService, ApiError } from '../services/api';
import { isMockMode, logger } from '../constants/config';

interface UseChatReturn {
  messages: Message[];
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
  sendMessage: (query: string) => Promise<void>;
  startNewSession: () => Promise<void>;
  clearError: () => void;
}

export const useChat = (): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Generate unique message ID
  const generateMessageId = () => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // Clear error message
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Start new session
  const startNewSession = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      logger.info('Starting new session...', { mockMode: isMockMode() });
      
      // Cancel any ongoing requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      // Clear messages and create new session
      setMessages([]);
      
      // Bỏ qua health check để user luôn có thể thấy chat input
      // Health check sẽ được thực hiện khi gửi message thực tế
      
      const newSessionId = await ApiService.createSession();
      setSessionId(newSessionId);
      logger.info('New session created:', newSessionId);
      
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'Có lỗi xảy ra khi tạo phiên mới';
      setError(errorMessage);
      logger.error('Error starting new session:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Send message with streaming
  const sendMessage = useCallback(async (query: string) => {
    if (!sessionId || isLoading) {
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      // Cancel any ongoing requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      abortControllerRef.current = new AbortController();

      // Add user message
      const userMessage: Message = {
        id: generateMessageId(),
        role: 'user',
        content: query,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage]);

      // Create assistant message for streaming
      const assistantMessageId = generateMessageId();
      const assistantMessage: Message = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Stream response
      let accumulatedContent = '';
      
      try {
        for await (const chunk of ApiService.streamChat(sessionId, query)) {
          // Check if request was aborted
          if (abortControllerRef.current?.signal.aborted) {
            break;
          }
          
          accumulatedContent += chunk;
          
          // Update the assistant message with accumulated content
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, content: accumulatedContent, isStreaming: true }
                : msg
            )
          );
        }
        
        // Mark streaming as complete
        setMessages(prev => 
          prev.map(msg => 
            msg.id === assistantMessageId 
              ? { ...msg, isStreaming: false }
              : msg
          )
        );
        
      } catch (streamError) {
        if (streamError instanceof ApiError) {
          setError(streamError.message);
        } else {
          setError('Có lỗi xảy ra khi nhận phản hồi');
        }
        
        // Remove the incomplete assistant message
        setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId));
      }
      
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'Có lỗi xảy ra khi gửi tin nhắn';
      setError(errorMessage);
      console.error('Error sending message:', err);
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [sessionId, isLoading]);

  // Initialize session on mount
  useEffect(() => {
    startNewSession();
    
    // Cleanup on unmount
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [startNewSession]);

  // Handle page visibility change to reconnect if needed
  useEffect(() => {
    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'visible' && sessionId && !isLoading) {
        // Check if backend is still healthy when page becomes visible
        const isHealthy = await ApiService.healthCheck();
        if (!isHealthy) {
          setError('Mất kết nối với server. Vui lòng tạo phiên mới.');
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [sessionId, isLoading]);

  return {
    messages,
    sessionId,
    isLoading,
    error,
    sendMessage,
    startNewSession,
    clearError,
  };
};
