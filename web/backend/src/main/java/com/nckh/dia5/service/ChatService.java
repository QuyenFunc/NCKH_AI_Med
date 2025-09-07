package com.nckh.dia5.service;

import com.nckh.dia5.model.ChatMessage;
import com.nckh.dia5.model.ChatSession;
import com.nckh.dia5.model.User;
import com.nckh.dia5.repository.ChatMessageRepository;
import com.nckh.dia5.repository.ChatSessionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatService {

    private final RestTemplate restTemplate;
    private final ChatSessionRepository chatSessionRepository;
    private final ChatMessageRepository chatMessageRepository;
    private final AuthService authService;

    @Value("${chatbot.service.url}")
    private String chatbotServiceUrl;

    /**
     * Tạo session chat mới
     */
    public ChatSession createChatSession() {
        try {
            User currentUser = authService.getCurrentUser();

            ChatSession session = new ChatSession();
            session.setId(UUID.randomUUID().toString());
            session.setUser(currentUser);
            session.setSessionType(ChatSession.SessionType.symptom_check);
            session.setStartedAt(LocalDateTime.now());
            session.setTotalMessages(0);

            ChatSession savedSession = chatSessionRepository.save(session);
            log.info("Created new chat session: {} for user: {}", savedSession.getId(), currentUser.getId());

            return savedSession;
        } catch (Exception e) {
            log.error("Error creating chat session", e);
            throw new RuntimeException("Không thể tạo phiên chat: " + e.getMessage());
        }
    }

    /**
     * Lưu user message vào database
     */
    public ChatMessage saveUserMessage(String sessionId, String messageText) {
        try {
            ChatSession session = getChatSession(sessionId);

            ChatMessage message = new ChatMessage();
            message.setSession(session);
            message.setMessageOrder(session.getTotalMessages() + 1);
            message.setSender(ChatMessage.Sender.user);
            message.setMessageText(messageText);
            message.setMessageType(ChatMessage.MessageType.text);
            message.setTimestamp(LocalDateTime.now());
            message.setContainsUrgencyKeywords(containsUrgencyKeywords(messageText));

            ChatMessage savedMessage = chatMessageRepository.save(message);

            // Cập nhật session
            session.setTotalMessages(session.getTotalMessages() + 1);
            chatSessionRepository.save(session);

            log.info("Saved user message for session: {}", sessionId);
            return savedMessage;

        } catch (Exception e) {
            log.error("Error saving user message for session: {}", sessionId, e);
            throw new RuntimeException("Không thể lưu tin nhắn: " + e.getMessage());
        }
    }

    /**
     * Lưu AI response vào database
     */
    public ChatMessage saveAiMessage(String sessionId, String messageText,
            Double confidence, Integer processingTime) {
        try {
            ChatSession session = getChatSession(sessionId);

            ChatMessage message = new ChatMessage();
            message.setSession(session);
            message.setMessageOrder(session.getTotalMessages() + 1);
            message.setSender(ChatMessage.Sender.ai);
            message.setMessageText(messageText);
            message.setMessageType(ChatMessage.MessageType.text);
            message.setTimestamp(LocalDateTime.now());

            if (confidence != null) {
                message.setAiConfidence(java.math.BigDecimal.valueOf(confidence));
            }
            if (processingTime != null) {
                message.setProcessingTimeMs(processingTime);
            }

            ChatMessage savedMessage = chatMessageRepository.save(message);

            // Cập nhật session
            session.setTotalMessages(session.getTotalMessages() + 1);
            chatSessionRepository.save(session);

            log.info("Saved AI message for session: {}", sessionId);
            return savedMessage;

        } catch (Exception e) {
            log.error("Error saving AI message for session: {}", sessionId, e);
            throw new RuntimeException("Không thể lưu phản hồi AI: " + e.getMessage());
        }
    }

    /**
     * Gọi Python chatbot service để get streaming response
     */
    public void sendToChatbot(String sessionId, String query) {
        try {
            String url = chatbotServiceUrl + "/chat/stream";

            Map<String, Object> requestBody = Map.of(
                    "query", query,
                    "session_id", sessionId);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("User-Agent", "Dia5-Backend/1.0");

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            log.info("Sending request to chatbot service: {} for session: {}", url, sessionId);

            // Gọi async - không chờ response ở đây vì là streaming
            // Frontend sẽ connect trực tiếp tới Python service để nhận stream
            restTemplate.postForEntity(url, entity, String.class);

        } catch (Exception e) {
            log.error("Error calling chatbot service for session: {}", sessionId, e);
            // Không throw exception vì đây chỉ là notification
        }
    }

    /**
     * Lấy lịch sử chat của session
     */
    public List<ChatMessage> getChatHistory(String sessionId) {
        try {
            ChatSession session = getChatSession(sessionId);
            return chatMessageRepository.findBySessionOrderByMessageOrderAsc(session);
        } catch (Exception e) {
            log.error("Error getting chat history for session: {}", sessionId, e);
            throw new RuntimeException("Không thể lấy lịch sử chat: " + e.getMessage());
        }
    }

    /**
     * Lấy danh sách sessions của user
     */
    public List<ChatSession> getUserSessions() {
        try {
            User currentUser = authService.getCurrentUser();
            return chatSessionRepository.findByUserOrderByStartedAtDesc(currentUser);
        } catch (Exception e) {
            log.error("Error getting user sessions", e);
            throw new RuntimeException("Không thể lấy danh sách phiên chat: " + e.getMessage());
        }
    }

    /**
     * Kết thúc session
     */
    public void endSession(String sessionId) {
        try {
            ChatSession session = getChatSession(sessionId);
            session.setEndedAt(LocalDateTime.now());
            chatSessionRepository.save(session);
            log.info("Ended chat session: {}", sessionId);
        } catch (Exception e) {
            log.error("Error ending session: {}", sessionId, e);
            throw new RuntimeException("Không thể kết thúc phiên chat: " + e.getMessage());
        }
    }

    /**
     * Delete chat session
     */
    public void deleteChatSession(String sessionId) {
        User currentUser = authService.getCurrentUser();
        ChatSession session = chatSessionRepository.findByIdAndUser(sessionId, currentUser)
                .orElseThrow(() -> new IllegalArgumentException("Không tìm thấy phiên chat: " + sessionId));

        // Delete all messages in the session first
        List<ChatMessage> messages = chatMessageRepository.findBySessionOrderByMessageOrderAsc(session);
        chatMessageRepository.deleteAll(messages);

        // Delete the session
        chatSessionRepository.delete(session);
        log.info("Deleted session {} with {} messages", sessionId, messages.size());
    }

    /**
     * Health check chatbot service
     */
    public boolean isChatbotServiceHealthy() {
        try {
            String url = chatbotServiceUrl + "/health";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getStatusCode() == HttpStatus.OK;
        } catch (Exception e) {
            log.warn("Chatbot service health check failed", e);
            return false;
        }
    }

    // Helper methods
    private ChatSession getChatSession(String sessionId) {
        User currentUser = authService.getCurrentUser();
        return chatSessionRepository.findByIdAndUser(sessionId, currentUser)
                .orElseGet(() -> {
                    // Tự động tạo session nếu không tồn tại
                    log.info("Session {} not found, creating new session for user {}", sessionId, currentUser.getId());
                    ChatSession newSession = new ChatSession();
                    newSession.setId(sessionId);
                    newSession.setUser(currentUser);
                    newSession.setSessionType(ChatSession.SessionType.general_question);
                    newSession.setStartedAt(LocalDateTime.now());
                    newSession.setTotalMessages(0);
                    return chatSessionRepository.save(newSession);
                });
    }

    private boolean containsUrgencyKeywords(String text) {
        String lowerText = text.toLowerCase();
        String[] urgencyKeywords = {
                "khẩn cấp", "cấp cứu", "đau dữ dội", "không thở được",
                "ngất", "bất tỉnh", "co giật", "chảy máu", "nguy hiểm"
        };

        for (String keyword : urgencyKeywords) {
            if (lowerText.contains(keyword)) {
                return true;
            }
        }
        return false;
    }
}
