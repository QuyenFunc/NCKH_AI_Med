package com.nckh.dia5.dto.chat;

import com.nckh.dia5.model.ChatMessage;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatMessageResponse {
    private Long id;
    private Integer messageOrder;
    private String sender;
    private String messageText;
    private String messageType;
    private Double aiConfidence;
    private Integer processingTimeMs;
    private Double sentimentScore;
    private Boolean containsUrgencyKeywords;
    private String sourcesJson; // ✅ NEW: Sources as JSON string
    private LocalDateTime timestamp;

    /**
     * Convert ChatMessage entity to ChatMessageResponse DTO
     */
    public static ChatMessageResponse fromEntity(ChatMessage message) {
        return ChatMessageResponse.builder()
                .id(message.getId().longValue())
                .messageOrder(message.getMessageOrder())
                .sender(message.getSender().name())
                .messageText(message.getMessageText())
                .messageType(message.getMessageType().name())
                .aiConfidence(message.getAiConfidence() != null ? message.getAiConfidence().doubleValue() : null)
                .processingTimeMs(message.getProcessingTimeMs())
                .sentimentScore(message.getSentimentScore() != null ? message.getSentimentScore().doubleValue() : null)
                .containsUrgencyKeywords(message.getContainsUrgencyKeywords())
                .sourcesJson(message.getSourcesJson()) // ✅ NEW: Map sources
                .timestamp(message.getTimestamp())
                .build();
    }
}
