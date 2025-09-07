package com.nckh.dia5.dto.medical;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiDiagnosisResponse {

    private String sessionId;
    private List<DiagnosisResult> results;
    private List<String> recommendations;
    private String urgencyLevel; // emergency, urgent, routine, self_care
    private Double primaryConfidence; // 0.0 to 1.0
    private Boolean needsSpecialistReferral;
    private Boolean needsFollowUp;
    private String followUpTimeframe;
    private Integer processingTimeMs;
    private String aiModelVersion;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DiagnosisResult {
        private String conditionName;
        private String icdCode;
        private Double confidence;
        private String reasoning;
        private List<String> symptoms;
        private String specialtyRecommended;
    }
}