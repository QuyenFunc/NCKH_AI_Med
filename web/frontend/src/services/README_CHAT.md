# Chat Streaming Service

## Tích hợp với medical_chatbot_enhanced.py

### ChatService

Service để tích hợp với backend medical chatbot streaming API.

#### API Endpoint:

- **URL**: `http://localhost:5001/chat/stream`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "query": "câu hỏi của user",
    "session_id": "session_id hoặc null"
  }
  ```
- **Response Type**: `text/event-stream`

#### Stream Format:

1. **Chunks**: `data: {"chunk": "từng_từ ", "word_index": 0, ...}\n\n`
2. **Final**: `data: {"type": "final", "confidence": 0.9, "sources": [...]}\n\n`
3. **End**: `data: [DONE]\n\n`

### Cách sử dụng:

```typescript
import { ChatService } from "./chat.service";

// Stream chat
const abortController = await ChatService.streamChat(
  "Tôi bị đau đầu",
  sessionId,
  {
    onChunk: (chunkData) => {
      console.log("Received chunk:", chunkData.chunk);
      // Cập nhật UI với chunk mới
    },
    onComplete: (finalData) => {
      console.log("Final data:", finalData);
      // Hiển thị confidence score và sources
    },
    onError: (error) => {
      console.error("Stream error:", error);
      // Xử lý lỗi
    },
  }
);

// Cancel stream nếu cần
abortController.abort();
```

### Features được implement:

- ✅ **Streaming Response**: Hiển thị từng từ khi AI trả lời
- ✅ **Real-time Updates**: Cập nhật UI ngay lập tức
- ✅ **Metadata Display**: Hiển thị confidence score và sources
- ✅ **Error Handling**: Xử lý lỗi connection và parsing
- ✅ **Abort Capability**: Có thể cancel request
- ✅ **Health Check**: Kiểm tra trạng thái backend
- ✅ **Session Management**: Quản lý session ID

### Components đã cập nhật:

1. **ChatService**: Core streaming logic
2. **useChat Hook**: Tích hợp streaming vào React state
3. **Message Component**: Hiển thị streaming indicator và metadata
4. **Types**: Định nghĩa interfaces cho streaming data

### Cấu trúc dữ liệu:

```typescript
// Chunk data từ stream
interface ChatChunkData {
  chunk: string;
  word_index: number;
}

// Final data khi stream kết thúc
interface ChatFinalData {
  type: "final";
  confidence: number;
  sources: ChatSource[];
}

// Source information
interface ChatSource {
  title: string;
  url?: string;
  content: string;
  confidence?: number;
}
```

### Test:

1. **Start backend**:

   ```bash
   cd chatbox
   python medical_chatbot_enhanced.py
   ```

2. **Start frontend**:

   ```bash
   cd frontend
   npm run dev
   ```

3. **Test streaming**: Gửi tin nhắn và quan sát:
   - Hiệu ứng gõ chữ real-time
   - Confidence score hiển thị sau khi hoàn thành
   - Sources references nếu có
   - Loading indicator khi đang stream
