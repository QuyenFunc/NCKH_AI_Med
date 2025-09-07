import { useState, useCallback, useEffect, useRef } from 'react';
import type { Message, ChatMetadata } from '../types';
import { ApiError } from '../services/api';
import { ChatService } from '../services/chat.service';
import { BackendService, type BackendChatMessage } from '../services/backend.service';
import { isMockMode, logger } from '../constants/config';

interface UseChatReturn {
  messages: Message[];
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
  sendMessage: (query: string) => Promise<void>;
  startNewSession: (forceNew?: boolean) => Promise<string | null>;
  loadExistingSession: (sessionId: string) => Promise<void>; // ✅ Add this
  clearError: () => void;
  onSessionCreated?: (sessionId: string) => void; // ✅ Callback for new session
}

// ✅ localStorage keys
const STORAGE_KEY_SESSION_ID = 'chat_session_id';

// ✅ Session persistence utilities
const saveSessionToStorage = (sessionId: string) => {
  try {
    localStorage.setItem(STORAGE_KEY_SESSION_ID, sessionId);
    logger.info('Session saved to localStorage:', sessionId);
  } catch (error) {
    logger.warn('Failed to save session to localStorage:', error);
  }
};

const loadSessionFromStorage = (): string | null => {
  try {
    const savedSessionId = localStorage.getItem(STORAGE_KEY_SESSION_ID);
    if (savedSessionId) {
      logger.info('Session loaded from localStorage:', savedSessionId);
      return savedSessionId;
    }
  } catch (error) {
    logger.warn('Failed to load session from localStorage:', error);
  }
  return null;
};

const clearSessionFromStorage = () => {
  try {
    localStorage.removeItem(STORAGE_KEY_SESSION_ID);
    logger.info('Session cleared from localStorage');
  } catch (error) {
    logger.warn('Failed to clear session from localStorage:', error);
  }
};

export const useChat = (onSessionCreated?: (sessionId: string) => void): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false); // ✅ Track if hook is initialized
  const abortControllerRef = useRef<AbortController | null>(null);
  const lastMessageRef = useRef<string | null>(null);
  const isStreamingCompleteRef = useRef<boolean>(false);

  // Generate unique message ID
  const generateMessageId = () => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // ✅ Convert BackendChatMessage to Message format
  const convertBackendMessage = (backendMsg: BackendChatMessage): Message => {
    const metadata: ChatMetadata = {};
    
    if (backendMsg.aiConfidence !== undefined) {
      metadata.confidence = backendMsg.aiConfidence;
    }
    
    if (backendMsg.processingTimeMs !== undefined) {
      metadata.processingTime = backendMsg.processingTimeMs;
    }
    
    return {
      id: `backend_${backendMsg.id}`,
      role: backendMsg.sender === 'ai' ? 'assistant' : 'user',
      content: backendMsg.messageText,
      timestamp: new Date(backendMsg.timestamp),
      metadata: Object.keys(metadata).length > 0 ? metadata : undefined
    };
  };

  // ✅ Load chat history from backend
  const loadChatHistory = useCallback(async (sessionId: string) => {
    try {
      logger.info('Loading chat history for session:', sessionId);
      const backendMessages = await BackendService.getChatHistory(sessionId);
      
      // Convert backend messages to frontend format
      const convertedMessages = backendMessages.map(convertBackendMessage);
      
      // Sort by timestamp to ensure correct order
      convertedMessages.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
      
      setMessages(convertedMessages);
      logger.info(`✅ Loaded ${convertedMessages.length} messages from history for session: ${sessionId}`);
      
    } catch (error) {
      logger.error('❌ Failed to load chat history for session:', sessionId, error);
      // Set empty messages array if load fails
      setMessages([]);
      // Don't set error state here to avoid blocking UI
    }
  }, []);

  // Clear error message
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Start new session
  const startNewSession = useCallback(async (forceNew: boolean = false): Promise<string | null> => {
    try {
      setIsLoading(true);
      setError(null);
      logger.info('Starting new session...', { mockMode: isMockMode() });
      
      // Cancel any ongoing requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      // ✅ Create new session if forced or if current session has messages
      if (forceNew || messages.length > 0) {
        logger.info('Creating new session', { forceNew, hasMessages: messages.length > 0 });
        // Clear messages and create new session
        setMessages([]);
        clearSessionFromStorage(); // ✅ Clear saved session
      } else {
        logger.info('Current session is empty, reusing existing session');
        setIsLoading(false);
        return sessionId; // Return current sessionId
      }
      
      try {
        // Tạo session qua Spring Boot backend
        const backendSession = await BackendService.createChatSession();
        setSessionId(backendSession.id);
        logger.info('New backend session created:', backendSession.id);
        // ✅ Notify callback about new session
        onSessionCreated?.(backendSession.id);
        return backendSession.id;
      } catch (backendError) {
        logger.warn('Backend session creation failed, using fallback:', backendError);
        // Fallback to client-side session ID
        const fallbackSessionId = ChatService.generateSessionId();
        setSessionId(fallbackSessionId);
        logger.info('Fallback session created:', fallbackSessionId);
        // ✅ Notify callback about new session
        onSessionCreated?.(fallbackSessionId);
        return fallbackSessionId;
      }
      
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'Có lỗi xảy ra khi tạo phiên mới';
      setError(errorMessage);
      logger.error('Error starting new session:', err);
    } finally {
      setIsLoading(false);
    }
    return null; // Return null if error
  }, [messages, sessionId]);

  // ✅ Load existing session (with history)
  const loadExistingSession = useCallback(async (existingSessionId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      logger.info('Loading existing session:', existingSessionId);
      
      // Cancel any ongoing requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      // Clear current messages first
      setMessages([]);
      
      setSessionId(existingSessionId);
      
      // ✅ Load chat history for existing session
      await loadChatHistory(existingSessionId);
      
    } catch (error) {
      logger.error('Failed to load existing session:', error);
      setError('Không thể tải phiên chat');
    } finally {
      setIsLoading(false);
    }
  }, [loadChatHistory]);


  // ✅ Save sessionId to localStorage when it changes
  useEffect(() => {
    if (sessionId && isInitialized) {
      saveSessionToStorage(sessionId);
    }
  }, [sessionId, isInitialized]);

  // ✅ Load chat history when sessionId changes (for manual session loads)
  useEffect(() => {
    if (sessionId && isInitialized) {
      // Always load history when sessionId changes (except during initialization)
      logger.info('SessionId changed, loading history for:', sessionId);
      loadChatHistory(sessionId);
    }
  }, [sessionId, loadChatHistory, isInitialized]);

  // Send message with streaming
  const sendMessage = useCallback(async (query: string) => {
    if (isLoading) {
      logger.warn('Cannot send message: already loading');
      return;
    }

    // ✅ Auto-create session if none exists (like ChatGPT)
    if (!sessionId) {
      logger.info('No session exists, creating new one automatically');
      const newSessionId = await startNewSession(false); // ✅ Don't force, use normal logic
      if (!newSessionId) {
        logger.error('Failed to create session');
        setError('Không thể tạo phiên chat mới');
        return;
      }
    }

    // ✅ Prevent duplicate messages
    if (lastMessageRef.current === query) {
      logger.warn('Duplicate message detected, ignoring');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      lastMessageRef.current = query;
      
      // Cancel any ongoing requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      logger.info('🚀 Starting new chat session');

      // Add user message
      const userMessage: Message = {
        id: generateMessageId(),
        role: 'user',
        content: query,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage]);

      // NO backend call here! Stream directly from Python chatbot first

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

      // ✅ Reset variables for each new chat
      let accumulatedContent = '';
      let chatMetadata: ChatMetadata = {};
      isStreamingCompleteRef.current = false;

      // Stream response với ChatService mới
      try {
        abortControllerRef.current = await ChatService.streamChat(
          query,
          sessionId,
          {
            onChunk: (chunkData) => {
              // Check if request was aborted or already completed
              if (abortControllerRef.current?.signal.aborted || isStreamingCompleteRef.current) {
                return;
              }
              
              accumulatedContent += chunkData.chunk;
              
              // Update the assistant message with accumulated content
              setMessages(prev => 
                prev.map(msg => 
                  msg.id === assistantMessageId 
                    ? { ...msg, content: accumulatedContent, isStreaming: true }
                    : msg
                )
              );
            },
            
            onComplete: async (finalData) => {
              // ✅ Mark streaming as complete to prevent race conditions
              isStreamingCompleteRef.current = true;
              
              // Cập nhật metadata từ final data
              chatMetadata = {
                confidence: finalData.confidence,
                sources: finalData.sources || [],
                processingTime: finalData.processing_time || 0
              };
              
              // NOW save both messages to backend after streaming is complete
              try {
                // Save user message first
                if (sessionId) {
                  await BackendService.sendUserMessage(sessionId, query);
                  logger.info('User message saved to backend');
                  
                  // Then save AI response (only if we have content)
                  if (accumulatedContent && accumulatedContent.trim().length > 0) {
                    await BackendService.saveAiResponse(
                      sessionId, 
                      accumulatedContent,
                      finalData.confidence,
                      finalData.processing_time || 0
                    );
                  } else {
                    logger.warn('No content to save for AI response');
                  }
                  logger.info('AI response saved to backend');
                } else {
                  logger.warn('No session ID available to save messages');
                }
              } catch (backendError) {
                logger.warn('Failed to save messages to backend:', backendError);
                // Không fail UX
              }
              
              // Mark streaming as complete với metadata
              setMessages(prev => 
                prev.map(msg => 
                  msg.id === assistantMessageId 
                    ? { 
                        ...msg, 
                        content: accumulatedContent,
                        isStreaming: false,
                        metadata: chatMetadata
                      }
                    : msg
                )
              );
              
              console.log('✅ Chat streaming completed with metadata:', chatMetadata);
            },
            
            onError: (error) => {
              // ✅ Mark streaming as complete on error
              isStreamingCompleteRef.current = true;
              
              console.error('❌ Chat streaming error:', error);
              setError(error.message || 'Có lỗi xảy ra khi nhận phản hồi');
              
              // Remove the incomplete assistant message
              setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId));
            }
          }
        );
        
      } catch (streamError) {
        console.error('❌ Stream initialization error:', streamError);
        if (streamError instanceof ApiError) {
          setError(streamError.message);
        } else if (streamError instanceof Error) {
          setError(streamError.message);
        } else {
          setError('Có lỗi xảy ra khi nhận phản hồi');
        }
        
        // Remove the incomplete assistant message
        setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId));
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Có lỗi xảy ra khi gửi tin nhắn';
      setError(errorMessage);
      console.error('Error sending message:', err);
    } finally {
      setIsLoading(false);
      // ✅ Clear last message ref after completion
      lastMessageRef.current = null;
      // ✅ Reset streaming complete flag for next message
      isStreamingCompleteRef.current = false;
    }
  }, [sessionId, isLoading, startNewSession]);

  // ✅ Initialize session on mount - only if no existing session
  useEffect(() => {
    if (!isInitialized) {
      const savedSessionId = loadSessionFromStorage();
      if (savedSessionId) {
        logger.info('Found saved session, loading:', savedSessionId);
        loadExistingSession(savedSessionId);
      } else {
        // ✅ Don't auto-create session on mount - let user start when they want
        logger.info('No saved session, waiting for user to start chat');
        setSessionId(null);
      }
      setIsInitialized(true);
    }
    
    // Cleanup on unmount
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [isInitialized, loadExistingSession]);

  // Handle page visibility change to reconnect if needed
  useEffect(() => {
    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'visible' && sessionId && !isLoading) {
        // Check if both chat service and backend are healthy
        const [chatHealthy, backendHealthy] = await Promise.all([
          ChatService.healthCheck(),
          BackendService.healthCheck()
        ]);
        
        if (!chatHealthy) {
          setError('Mất kết nối với chat server. Vui lòng tạo phiên mới.');
        } else if (!backendHealthy) {
          logger.warn('Backend is not healthy, but continuing with chat service only');
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
    loadExistingSession, // ✅ Add this
    clearError,
  };
};
