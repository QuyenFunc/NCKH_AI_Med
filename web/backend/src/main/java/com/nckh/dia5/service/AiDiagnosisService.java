package com.nckh.dia5.service;

import com.nckh.dia5.dto.medical.AiDiagnosisRequest;
import com.nckh.dia5.dto.medical.AiDiagnosisResponse;
import com.nckh.dia5.model.AiDiagnosis;
import com.nckh.dia5.model.User;
import com.nckh.dia5.model.UserSymptomReport;
import com.nckh.dia5.repository.AiDiagnosisRepository;
import com.nckh.dia5.repository.UserSymptomReportRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class AiDiagnosisService {

    private final RestTemplate restTemplate;
    private final AiDiagnosisRepository aiDiagnosisRepository;
    private final UserSymptomReportRepository symptomReportRepository;
    private final AuthService authService;

    @Value("${ai.diagnosis.service.url}")
    private String aiServiceUrl;

    @Value("${ai.diagnosis.service.api-key}")
    private String apiKey;

    public AiDiagnosisResponse getDiagnosis(String sessionId) {
        try {
            log.info("Getting AI diagnosis for session: {}", sessionId);

            // Lấy thông tin user hiện tại
            User currentUser = authService.getCurrentUser();

            // Lấy các symptom reports trong session
            List<UserSymptomReport> symptoms = symptomReportRepository
                    .findByUserAndSessionIdOrderByReportedAtDesc(currentUser, sessionId);

            if (symptoms.isEmpty()) {
                throw new IllegalArgumentException("Không tìm thấy triệu chứng trong session: " + sessionId);
            }

            // Chuẩn bị request data
            AiDiagnosisRequest request = buildDiagnosisRequest(currentUser, symptoms, sessionId);

            // Gọi AI service
            AiDiagnosisResponse aiResponse = callAiService(request);

            // Lưu kết quả vào database
            saveAiDiagnosis(currentUser, sessionId, aiResponse);

            return aiResponse;

        } catch (Exception e) {
            log.error("Error getting AI diagnosis for session: {}", sessionId, e);
            throw new RuntimeException("Lỗi khi gọi AI chẩn đoán: " + e.getMessage());
        }
    }

    private AiDiagnosisRequest buildDiagnosisRequest(User user, List<UserSymptomReport> symptoms, String sessionId) {
        // Build user profile
        AiDiagnosisRequest.UserProfile userProfile = AiDiagnosisRequest.UserProfile.builder()
                .age(calculateAge(user.getDemographics()))
                .gender(user.getDemographics() != null ? user.getDemographics().getGender().toString() : null)
                .heightCm(user.getDemographics() != null ? user.getDemographics().getHeightCm() : null)
                .weightKg(user.getDemographics() != null ? user.getDemographics().getWeightKg().doubleValue() : null)
                .province(user.getDemographics() != null && user.getDemographics().getProvince() != null
                        ? user.getDemographics().getProvince().getName()
                        : null)
                .medicalHistory(getUserMedicalHistory(user))
                .allergies(getUserAllergies(user))
                .currentMedications(getUserCurrentMedications(user))
                .build();

        // Build symptoms info
        List<AiDiagnosisRequest.SymptomInfo> symptomInfos = symptoms.stream()
                .map(this::convertToSymptomInfo)
                .collect(Collectors.toList());

        return AiDiagnosisRequest.builder()
                .sessionId(sessionId)
                .userId(user.getId())
                .userProfile(userProfile)
                .symptoms(symptomInfos)
                .additionalContext("Chẩn đoán y tế thông qua ứng dụng Dia5")
                .build();
    }

    private AiDiagnosisResponse callAiService(AiDiagnosisRequest request) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("X-API-Key", apiKey);
            headers.set("User-Agent", "Dia5-Medical-App/1.0");

            HttpEntity<AiDiagnosisRequest> entity = new HttpEntity<>(request, headers);

            log.info("Calling AI service at: {}", aiServiceUrl + "/diagnosis");

            ResponseEntity<AiDiagnosisResponse> response = restTemplate.postForEntity(
                    aiServiceUrl + "/diagnosis",
                    entity,
                    AiDiagnosisResponse.class);

            if (response.getStatusCode() == HttpStatus.OK) {
                return response.getBody();
            } else {
                throw new RuntimeException("AI service returned status: " + response.getStatusCode());
            }

        } catch (Exception e) {
            log.error("Error calling AI service", e);
            throw new RuntimeException("Không thể kết nối đến AI service: " + e.getMessage());
        }
    }

    private void saveAiDiagnosis(User user, String sessionId, AiDiagnosisResponse response) {
        try {
            AiDiagnosis diagnosis = AiDiagnosis.builder()
                    .user(user)
                    .sessionId(sessionId)
                    .diagnosisResults(response.getResults().toString()) // JSON string
                    .recommendations(String.join("; ", response.getRecommendations()))
                    .urgencyLevel(AiDiagnosis.UrgencyLevel.valueOf(response.getUrgencyLevel()))
                    .confidenceScore(response.getConfidenceScore())
                    .generatedAt(LocalDateTime.now())
                    .build();

            aiDiagnosisRepository.save(diagnosis);
            log.info("Saved AI diagnosis for user: {} session: {}", user.getId(), sessionId);

        } catch (Exception e) {
            log.error("Error saving AI diagnosis", e);
            // Không throw exception để không ảnh hưởng đến response
        }
    }

    // Helper methods
    private Integer calculateAge(User.UserDemographic demographics) {
        if (demographics == null || demographics.getBirthYear() == null) {
            return null;
        }
        return LocalDateTime.now().getYear() - demographics.getBirthYear();
    }

    private List<String> getUserMedicalHistory(User user) {
        // TODO: Implement based on your user medical history model
        return List.of();
    }

    private List<String> getUserAllergies(User user) {
        // TODO: Implement based on your user allergies model
        return List.of();
    }

    private List<String> getUserCurrentMedications(User user) {
        // TODO: Implement based on your user medications model
        return List.of();
    }

    private AiDiagnosisRequest.SymptomInfo convertToSymptomInfo(UserSymptomReport report) {
        return AiDiagnosisRequest.SymptomInfo.builder()
                .name(report.getSymptom() != null ? report.getSymptom().getName() : "Unknown")
                .severity(report.getSeverity())
                .durationHours(report.getDurationHours())
                .frequency(report.getFrequency() != null ? report.getFrequency().toString() : null)
                .location(report.getLocationBodyPart())
                .description(report.getQualityDescription())
                .triggers(report.getTriggers())
                .build();
    }

    public List<AiDiagnosis> getUserDiagnosisHistory() {
        User currentUser = authService.getCurrentUser();
        return aiDiagnosisRepository.findByUserOrderByGeneratedAtDesc(currentUser);
    }

    public AiDiagnosis getDiagnosisBySession(String sessionId) {
        User currentUser = authService.getCurrentUser();
        return aiDiagnosisRepository.findByUserAndSessionId(currentUser, sessionId)
                .orElseThrow(() -> new IllegalArgumentException("Không tìm thấy chẩn đoán cho session: " + sessionId));
    }
}
