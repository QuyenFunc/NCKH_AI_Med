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
public class AiDiagnosisRequest {

    private String sessionId;
    private String userId;
    private UserProfile userProfile;
    private List<SymptomInfo> symptoms;
    private String additionalContext;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class UserProfile {
        private Integer age;
        private String gender;
        private Integer heightCm;
        private Double weightKg;
        private String province;
        private List<String> medicalHistory;
        private List<String> allergies;
        private List<String> currentMedications;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SymptomInfo {
        private String name;
        private Integer severity;
        private Integer durationHours;
        private String frequency;
        private String location;
        private String description;
        private List<String> triggers;
    }
}
