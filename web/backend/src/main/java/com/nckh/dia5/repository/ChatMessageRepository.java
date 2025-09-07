package com.nckh.dia5.repository;

import com.nckh.dia5.model.ChatMessage;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ChatMessageRepository extends JpaRepository<ChatMessage, Integer> {

    @Query("SELECT cm FROM ChatMessage cm WHERE cm.session.id = :sessionId ORDER BY cm.messageOrder")
    List<ChatMessage> findBySessionIdOrderByOrder(@Param("sessionId") String sessionId);

    @Query("SELECT cm FROM ChatMessage cm WHERE cm.session.id = :sessionId ORDER BY cm.messageOrder")
    Page<ChatMessage> findBySessionId(@Param("sessionId") String sessionId, Pageable pageable);

    @Query("SELECT cm FROM ChatMessage cm WHERE cm.session.user.id = :userId ORDER BY cm.timestamp DESC")
    Page<ChatMessage> findByUserId(@Param("userId") String userId, Pageable pageable);

    @Query("SELECT cm FROM ChatMessage cm WHERE cm.sender = :sender AND cm.timestamp >= :since")
    List<ChatMessage> findBySenderSince(@Param("sender") ChatMessage.Sender sender,
            @Param("since") LocalDateTime since);

    @Query("SELECT cm FROM ChatMessage cm WHERE cm.messageType = :messageType")
    List<ChatMessage> findByMessageType(@Param("messageType") ChatMessage.MessageType messageType);

    @Query("SELECT cm FROM ChatMessage cm WHERE cm.containsUrgencyKeywords = true")
    List<ChatMessage> findUrgentMessages();

    @Query("SELECT COUNT(cm) FROM ChatMessage cm WHERE cm.session.id = :sessionId")
    Long countBySessionId(@Param("sessionId") String sessionId);

    @Query("SELECT AVG(cm.aiConfidence) FROM ChatMessage cm WHERE cm.sender = 'ai' AND cm.aiConfidence IS NOT NULL")
    Double findAverageAiConfidence();
}
