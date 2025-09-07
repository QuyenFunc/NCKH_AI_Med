package com.nckh.dia5.repository;

import com.nckh.dia5.model.ChatSession;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ChatSessionRepository extends JpaRepository<ChatSession, String> {

    @Query("SELECT cs FROM ChatSession cs WHERE cs.user.id = :userId ORDER BY cs.startedAt DESC")
    Page<ChatSession> findByUserId(@Param("userId") String userId, Pageable pageable);

    @Query("SELECT cs FROM ChatSession cs WHERE cs.sessionType = :sessionType ORDER BY cs.startedAt DESC")
    List<ChatSession> findBySessionType(@Param("sessionType") ChatSession.SessionType sessionType);

    @Query("SELECT cs FROM ChatSession cs WHERE cs.user.id = :userId AND cs.sessionType = :sessionType ORDER BY cs.startedAt DESC")
    List<ChatSession> findByUserIdAndSessionType(@Param("userId") String userId,
            @Param("sessionType") ChatSession.SessionType sessionType);

    @Query("SELECT cs FROM ChatSession cs WHERE cs.endedAt IS NULL")
    List<ChatSession> findActiveSessions();

    @Query("SELECT cs FROM ChatSession cs WHERE cs.user.id = :userId AND cs.endedAt IS NULL")
    List<ChatSession> findActiveSessionsByUserId(@Param("userId") String userId);

    @Query("SELECT cs FROM ChatSession cs WHERE cs.startedAt >= :since")
    List<ChatSession> findSessionsSince(@Param("since") LocalDateTime since);

    @Query("SELECT COUNT(cs) FROM ChatSession cs WHERE cs.user.id = :userId")
    Long countByUserId(@Param("userId") String userId);

    @Query("SELECT AVG(cs.satisfactionRating) FROM ChatSession cs WHERE cs.satisfactionRating IS NOT NULL")
    Double findAverageSatisfactionRating();
}
