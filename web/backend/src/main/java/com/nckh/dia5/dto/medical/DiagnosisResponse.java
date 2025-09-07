package com.nckh.dia5.dto.medical;

import com.nckh.dia5.model.AiDiagnosis;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DiagnosisResponse {
    private Integer id;
    private String sessionId;
    private String primaryDiagnosisName;
    private BigDecimal primaryConfidence;
    private List<DifferentialDiagnosis> differentialDiagnoses;
    private AiDiagnosis.UrgencyLevel urgencyLevel;
    private List<String> recommendedActions;
    private boolean specialistReferralNeeded;
    private String recommendedSpecialtyName;
    private boolean followUpNeeded;
    private String followUpTimeframe;
    private LocalDateTime createdAt;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DifferentialDiagnosis {
        private Integer diseaseId;
        private String diseaseName;
        private BigDecimal confidence;
        private String reasoning;
    }
}
