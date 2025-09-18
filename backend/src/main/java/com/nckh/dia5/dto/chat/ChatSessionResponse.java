package com.nckh.dia5.dto.chat;

import com.nckh.dia5.model.ChatSession;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatSessionResponse {
    private String id;
    private String sessionType;
    private LocalDateTime startedAt;
    private LocalDateTime endedAt;
    private Integer totalMessages;
    private Integer satisfactionRating;
    private Boolean wasHelpful;

    /**
     * Convert ChatSession entity to ChatSessionResponse DTO
     */
    public static ChatSessionResponse fromEntity(ChatSession session) {
        return ChatSessionResponse.builder()
                .id(session.getId())
                .sessionType(session.getSessionType().name())
                .startedAt(session.getStartedAt())
                .endedAt(session.getEndedAt())
                .totalMessages(session.getTotalMessages())
                .satisfactionRating(session.getSatisfactionRating())
                .wasHelpful(session.getWasHelpful())
                .build();
    }
}
