package com.nckh.dia5.controller;

import com.nckh.dia5.dto.common.ApiResponse;
import com.nckh.dia5.model.ChatMessage;
import com.nckh.dia5.model.ChatSession;
import com.nckh.dia5.service.ChatService;
import com.nckh.dia5.dto.chat.ChatSessionResponse;
import com.nckh.dia5.dto.chat.ChatMessageResponse;
import java.util.HashMap;
import java.util.Map;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    /**
     * Tạo phiên chat mới
     */
    @PostMapping("/sessions")
    public ResponseEntity<ApiResponse<Map<String, Object>>> createSession() {
        try {
            log.info("Creating new chat session");
            ChatSession session = chatService.createChatSession();

            // Create a simple response without Hibernate proxies
            Map<String, Object> sessionResponse = new HashMap<>();
            sessionResponse.put("id", session.getId());
            sessionResponse.put("sessionType", session.getSessionType());
            sessionResponse.put("startedAt", session.getStartedAt());
            sessionResponse.put("totalMessages", session.getTotalMessages());
            sessionResponse.put("userId", session.getUser().getId());

            return ResponseEntity.ok(ApiResponse.success(sessionResponse, "Tạo phiên chat thành công"));

        } catch (Exception e) {
            log.error("Error creating chat session", e);
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("Lỗi khi tạo phiên chat: " + e.getMessage(), 500));
        }
    }

    /**
     * Gửi tin nhắn từ user
     */
    @PostMapping("/sessions/{sessionId}/messages")
    public ResponseEntity<ApiResponse<Map<String, Object>>> sendMessage(
            @PathVariable @NotBlank String sessionId,
            @Valid @RequestBody SendMessageRequest request) {

        try {
            log.info("Sending message to session: {}", sessionId);

            // Lưu user message
            ChatMessage userMessage = chatService.saveUserMessage(sessionId, request.getMessage());

            // REMOVED: No longer sending to chatbot from backend
            // Frontend streams directly from Python chatbot to avoid duplicates

            // Create a simple response without Hibernate proxies
            Map<String, Object> messageResponse = new HashMap<>();
            messageResponse.put("id", userMessage.getId());
            messageResponse.put("messageText", userMessage.getMessageText());
            messageResponse.put("sender", userMessage.getSender());
            messageResponse.put("timestamp", userMessage.getTimestamp());
            messageResponse.put("sessionId", sessionId);

            return ResponseEntity.ok(ApiResponse.success(messageResponse, "Tin nhắn đã được gửi"));

        } catch (IllegalArgumentException e) {
            log.warn("Invalid session: {}", sessionId);
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error(e.getMessage(), 400));

        } catch (Exception e) {
            log.error("Error sending message to session: {}", sessionId, e);
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("Lỗi khi gửi tin nhắn: " + e.getMessage(), 500));
        }
    }

    /**
     * Lưu phản hồi từ AI (được gọi từ Python service hoặc frontend)
     */
    @PostMapping("/sessions/{sessionId}/ai-response")
    public ResponseEntity<ApiResponse<ChatMessage>> saveAiResponse(
            @PathVariable @NotBlank String sessionId,
            @Valid @RequestBody SaveAiResponseRequest request) {

        try {
            log.info("Saving AI response for session: {}", sessionId);

            // Validate message content
            String message = request.getMessage();
            if (message == null || message.trim().isEmpty()) {
                log.warn("Empty AI response message for session: {}", sessionId);
                return ResponseEntity.badRequest()
                        .body(ApiResponse.error("AI response message cannot be empty", 400));
            }

            ChatMessage aiMessage = chatService.saveAiMessage(
                    sessionId,
                    message,
                    request.getConfidence(),
                    request.getProcessingTime(),
                    request.getSourcesJson()); // ✅ NEW: Pass sources

            return ResponseEntity.ok(ApiResponse.success(aiMessage, "Phản hồi AI đã được lưu"));

        } catch (IllegalArgumentException e) {
            log.warn("Invalid session: {}", sessionId);
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error(e.getMessage(), 400));

        } catch (Exception e) {
            log.error("Error saving AI response for session: {}", sessionId, e);
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("Lỗi khi lưu phản hồi AI: " + e.getMessage(), 500));
        }
    }

    /**
     * Lấy lịch sử chat của session
     */
    @GetMapping("/sessions/{sessionId}/messages")
    public ResponseEntity<ApiResponse<List<ChatMessageResponse>>> getChatHistory(
            @PathVariable @NotBlank String sessionId) {

        try {
            log.info("Getting chat history for session: {}", sessionId);
            List<ChatMessage> messages = chatService.getChatHistory(sessionId);

            // ✅ Convert to DTO to avoid Hibernate proxy serialization issues
            List<ChatMessageResponse> messageResponses = messages.stream()
                    .map(ChatMessageResponse::fromEntity)
                    .collect(java.util.stream.Collectors.toList());

            return ResponseEntity.ok(ApiResponse.success(messageResponses));

        } catch (IllegalArgumentException e) {
            log.warn("Invalid session: {}", sessionId);
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error(e.getMessage(), 400));

        } catch (Exception e) {
            log.error("Error getting chat history for session: {}", sessionId, e);
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("Lỗi khi lấy lịch sử chat: " + e.getMessage(), 500));
        }
    }

    /**
     * Lấy danh sách sessions của user
     */
    @GetMapping("/sessions")
    public ResponseEntity<ApiResponse<List<ChatSessionResponse>>> getUserSessions() {
        try {
            log.info("Getting user chat sessions");
            List<ChatSession> sessions = chatService.getUserSessions();

            // ✅ Convert to DTO to avoid Hibernate proxy serialization issues
            List<ChatSessionResponse> sessionResponses = sessions.stream()
                    .map(ChatSessionResponse::fromEntity)
                    .collect(java.util.stream.Collectors.toList());

            return ResponseEntity.ok(ApiResponse.success(sessionResponses));

        } catch (Exception e) {
            log.error("Error getting user sessions", e);
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("Lỗi khi lấy danh sách phiên chat: " + e.getMessage(), 500));
        }
    }

    /**
     * Kết thúc session
     */
    @PutMapping("/sessions/{sessionId}/end")
    public ResponseEntity<ApiResponse<String>> endSession(
            @PathVariable @NotBlank String sessionId) {

        try {
            log.info("Ending chat session: {}", sessionId);
            chatService.endSession(sessionId);
            return ResponseEntity.ok(ApiResponse.success(null, "Phiên chat đã được kết thúc"));

        } catch (IllegalArgumentException e) {
            log.warn("Invalid session: {}", sessionId);
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error(e.getMessage(), 400));

        } catch (Exception e) {
            log.error("Error ending session: {}", sessionId, e);
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("Lỗi khi kết thúc phiên chat: " + e.getMessage(), 500));
        }
    }

    /**
     * Delete chat session
     */
    @DeleteMapping("/sessions/{sessionId}")
    public ResponseEntity<ApiResponse<String>> deleteSession(@PathVariable @NotBlank String sessionId) {
        try {
            log.info("Deleting session: {}", sessionId);
            chatService.deleteChatSession(sessionId);
            return ResponseEntity.ok(ApiResponse.success("Phiên chat đã được xóa", "Xóa phiên chat thành công"));
        } catch (IllegalArgumentException e) {
            log.warn("Invalid session: {}", sessionId);
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error(e.getMessage(), 400));
        } catch (Exception e) {
            log.error("Error deleting session: {}", sessionId, e);
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("Lỗi khi xóa phiên chat: " + e.getMessage(), 500));
        }
    }

    /**
     * Health check
     */
    @GetMapping("/health")
    public ResponseEntity<ApiResponse<Map<String, Object>>> healthCheck() {
        try {
            boolean chatbotHealthy = chatService.isChatbotServiceHealthy();

            Map<String, Object> health = Map.of(
                    "status", chatbotHealthy ? "healthy" : "unhealthy",
                    "chatbot_service", chatbotHealthy,
                    "timestamp", System.currentTimeMillis());

            return ResponseEntity.ok(ApiResponse.success(health));

        } catch (Exception e) {
            log.error("Error in health check", e);
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("Health check failed", 500));
        }
    }

    // Request DTOs
    public static class SendMessageRequest {
        @NotBlank(message = "Tin nhắn không được để trống")
        private String message;

        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }
    }

    public static class SaveAiResponseRequest {
        private String message;
        private Double confidence;
        private Integer processingTime;
        private String sourcesJson; // ✅ NEW: Sources as JSON string

        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }

        public Double getConfidence() {
            return confidence;
        }

        public void setConfidence(Double confidence) {
            this.confidence = confidence;
        }

        public Integer getProcessingTime() {
            return processingTime;
        }

        public void setProcessingTime(Integer processingTime) {
            this.processingTime = processingTime;
        }

        // ✅ NEW: Sources getter/setter
        public String getSourcesJson() {
            return sourcesJson;
        }

        public void setSourcesJson(String sourcesJson) {
            this.sourcesJson = sourcesJson;
        }
    }
}
