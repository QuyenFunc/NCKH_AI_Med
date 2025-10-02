package com.nckh.dia5.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "ai_diagnoses")
@Data
@NoArgsConstructor
@AllArgsConstructor
@EntityListeners(AuditingEntityListener.class)
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class AiDiagnosis {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private User user;

    @Column(name = "session_id", nullable = false, length = 36)
    private String sessionId; // Links to symptom report session

    // Primary diagnosis
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "primary_diagnosis_id")
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private DiseaseCategory primaryDiagnosis;

    @Column(name = "primary_confidence", precision = 5, scale = 2)
    private BigDecimal primaryConfidence; // 0-100% confidence

    // Differential diagnoses
    @Column(name = "differential_diagnoses", columnDefinition = "TEXT")
    private String differentialDiagnoses; // JSON array of {disease_id, confidence, reasoning}

    // Risk factors considered
    @Column(name = "risk_factors_applied", columnDefinition = "TEXT")
    private String riskFactorsApplied; // JSON array

    // Recommendations
    @Enumerated(EnumType.STRING)
    @Column(name = "urgency_level")
    private UrgencyLevel urgencyLevel;

    @Column(name = "recommended_actions", columnDefinition = "TEXT")
    private String recommendedActions; // JSON array

    @Column(name = "specialist_referral_needed", nullable = false)
    private Boolean specialistReferralNeeded = false;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "recommended_specialty_id")
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private MedicalSpecialty recommendedSpecialty;

    // AI model information
    @Column(name = "ai_model_version", length = 50)
    private String aiModelVersion;

    @Column(name = "processing_time_ms")
    private Integer processingTimeMs;

    // Follow-up
    @Column(name = "follow_up_needed", nullable = false)
    private Boolean followUpNeeded = false;

    @Column(name = "follow_up_timeframe", length = 50)
    private String followUpTimeframe; // "24 hours", "1 week", etc.

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public enum UrgencyLevel {
        emergency, urgent, routine, self_care
    }
}
