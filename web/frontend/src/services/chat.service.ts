import type { ChatStreamCallbacks, ChatChunkData, ChatFinalData } from '../types';

/**
 * Chat Service để tích hợp với medical_chatbot_enhanced.py streaming API
 */
export class ChatService {
  private static readonly CHAT_API_URL = 'http://localhost:5001/chat/stream';

  /**
   * Stream chat với backend medical chatbot
   * @param query Câu hỏi của user
   * @param sessionId Session ID (có thể null)
   * @param callbacks Callbacks để xử lý streaming data
   * @returns AbortController để có thể cancel request
   */
  static async streamChat(
    query: string,
    sessionId: string | null,
    callbacks: ChatStreamCallbacks
  ): Promise<AbortController> {
    const abortController = new AbortController();

    try {
      console.log('🚀 Starting stream chat:', { query, sessionId });

      const response = await fetch(this.CHAT_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          session_id: sessionId,
        }),
        signal: abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      // Kiểm tra content type
      const contentType = response.headers.get('content-type');
      if (!contentType?.includes('text/event-stream') && !contentType?.includes('text/plain')) {
        console.warn('⚠️ Unexpected content type:', contentType);
      }

      // Sử dụng TextDecoder để decode stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      console.log('📡 Starting to read stream...');

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          console.log('✅ Stream completed');
          break;
        }

        // Check if request was aborted
        if (abortController.signal.aborted) {
          console.log('🛑 Stream aborted');
          break;
        }

        // Decode chunk và thêm vào buffer
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;

        // Xử lý các SSE events trong buffer
        const events = buffer.split('\n\n');
        
        // Giữ lại phần cuối chưa hoàn chỉnh
        buffer = events.pop() || '';

        for (const event of events) {
          if (!event.trim()) continue;

          try {
            // Parse SSE event
            const lines = event.split('\n');
            let data = '';

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                data = line.substring(6);
                break;
              }
            }

            if (!data) continue;

            console.log('📥 Received data:', data);

            // Kiểm tra nếu là signal kết thúc
            if (data.trim() === '[DONE]') {
              console.log('🏁 Received [DONE] signal');
              return abortController;
            }

            // Parse JSON data
            let parsedData: any;
            try {
              parsedData = JSON.parse(data);
              console.log('📦 Parsed data:', parsedData);
            } catch (parseError) {
              console.warn('⚠️ Failed to parse JSON:', data, parseError);
              continue;
            }

            // Xử lý dữ liệu dựa trên type
            if (parsedData.type === 'final') {
              console.log('🎯 Received final data:', parsedData);
              callbacks.onComplete(parsedData as ChatFinalData);
            } else if (parsedData.type === 'error') {
              // ✅ Handle error type from backend
              console.error('❌ Received error from backend:', parsedData);
              callbacks.onError(new Error(parsedData.error || 'Unknown streaming error'));
            } else if (parsedData.chunk !== undefined) {
              // Đây là chunk data
              console.log('📝 Received chunk:', parsedData);
              callbacks.onChunk(parsedData as ChatChunkData);
            } else {
              console.log('⚠️ Unknown data format, treating as chunk:', parsedData);
              // Fallback: treat unknown format as chunk with the whole content
              if (parsedData.response) {
                callbacks.onChunk({ 
                  chunk: parsedData.response,
                  word_index: 0,
                  total_words: 1,
                  session_id: parsedData.session_id || 'unknown'
                } as ChatChunkData);
              }
            }
          } catch (eventError) {
            console.error('❌ Error processing event:', eventError);
          }
        }
      }

    } catch (error) {
      console.error('❌ Stream chat error:', error);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          console.log('⏹️ Stream aborted by user');
          return abortController;
        }
        callbacks.onError(error);
      } else {
        callbacks.onError(new Error('Unknown streaming error'));
      }
    }

    return abortController;
  }

  /**
   * Tạo session ID mới
   */
  static generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Health check cho chat service
   */
  static async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch('http://localhost:5001/health', {
        method: 'GET',
        signal: AbortSignal.timeout(5000), // 5s timeout
      });
      
      return response.ok;
    } catch (error) {
      console.warn('Chat service health check failed:', error);
      return false;
    }
  }
}

/**
 * Legacy wrapper để tương thích với ApiService.streamChat
 * @deprecated Sử dụng ChatService.streamChat thay thế
 */
export async function* legacyStreamChat(
  sessionId: string,
  query: string
): AsyncGenerator<string, void, unknown> {
  let accumulatedContent = '';
  let streamCompleted = false;

  const promise = new Promise<void>((resolve, reject) => {
    ChatService.streamChat(query, sessionId, {
      onChunk: (chunkData) => {
        accumulatedContent += chunkData.chunk;
      },
      onComplete: (finalData) => {
        streamCompleted = true;
        resolve();
      },
      onError: (error) => {
        reject(error);
      },
    });
  });

  // Yield accumulated content periodically
  let lastYieldedLength = 0;
  const yieldInterval = setInterval(() => {
    if (accumulatedContent.length > lastYieldedLength) {
      const newContent = accumulatedContent.slice(lastYieldedLength);
      lastYieldedLength = accumulatedContent.length;
      // Note: Generator doesn't work well with async intervals
      // This is a simplified implementation
    }
  }, 100);

  try {
    await promise;
    
    // Yield final content
    if (accumulatedContent.length > lastYieldedLength) {
      yield accumulatedContent.slice(lastYieldedLength);
    }
  } finally {
    clearInterval(yieldInterval);
  }
}
