package com.nckh.dia5.dto.medical;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiDiagnosisResponse {

    private String diagnosisId;
    private String sessionId;
    private List<DiagnosisResult> results;
    private List<String> recommendations;
    private String urgencyLevel;
    private Double confidenceScore;
    private LocalDateTime generatedAt;
    private String disclaimerMessage;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DiagnosisResult {
        private String diseaseName;
        private String diseaseCode;
        private Double probability;
        private String description;
        private String severity;
        private List<String> matchedSymptoms;
        private List<String> additionalQuestions;
        private String recommendedSpecialty;
        private Boolean requiresImmediateAttention;
    }
}
