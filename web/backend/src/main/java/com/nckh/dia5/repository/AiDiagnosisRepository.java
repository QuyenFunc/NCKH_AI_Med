package com.nckh.dia5.repository;

import com.nckh.dia5.model.AiDiagnosis;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface AiDiagnosisRepository extends JpaRepository<AiDiagnosis, Integer> {

    @Query("SELECT ad FROM AiDiagnosis ad WHERE ad.user.id = :userId ORDER BY ad.createdAt DESC")
    Page<AiDiagnosis> findByUserId(@Param("userId") String userId, Pageable pageable);

    Optional<AiDiagnosis> findBySessionId(String sessionId);

    @Query("SELECT ad FROM AiDiagnosis ad WHERE ad.user.id = :userId AND ad.sessionId = :sessionId")
    Optional<AiDiagnosis> findByUserIdAndSessionId(@Param("userId") String userId,
            @Param("sessionId") String sessionId);

    @Query("SELECT ad FROM AiDiagnosis ad WHERE ad.urgencyLevel = :urgencyLevel ORDER BY ad.createdAt DESC")
    List<AiDiagnosis> findByUrgencyLevel(@Param("urgencyLevel") AiDiagnosis.UrgencyLevel urgencyLevel);

    @Query("SELECT ad FROM AiDiagnosis ad WHERE ad.urgencyLevel IN ('emergency', 'urgent') ORDER BY ad.createdAt DESC")
    List<AiDiagnosis> findUrgentDiagnoses();

    @Query("SELECT ad FROM AiDiagnosis ad WHERE ad.followUpNeeded = true AND ad.createdAt <= :cutoffDate")
    List<AiDiagnosis> findDiagnosesNeedingFollowUp(@Param("cutoffDate") LocalDateTime cutoffDate);

    @Query("SELECT ad FROM AiDiagnosis ad WHERE ad.primaryDiagnosis.id = :diseaseId")
    List<AiDiagnosis> findByPrimaryDiagnosisId(@Param("diseaseId") Integer diseaseId);

    @Query("SELECT COUNT(ad) FROM AiDiagnosis ad WHERE ad.user.id = :userId")
    Long countByUserId(@Param("userId") String userId);

    @Query("SELECT ad FROM AiDiagnosis ad WHERE ad.user.id = :userId AND ad.createdAt >= :since")
    List<AiDiagnosis> findRecentByUserId(@Param("userId") String userId, @Param("since") LocalDateTime since);
}
