package com.nckh.dia5.controller;

import com.nckh.dia5.dto.common.ApiResponse;
import com.nckh.dia5.dto.medical.AiDiagnosisResponse;
import com.nckh.dia5.model.AiDiagnosis;
import com.nckh.dia5.service.AiDiagnosisService;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/ai-diagnosis")
@RequiredArgsConstructor
public class AiDiagnosisController {

    private final AiDiagnosisService aiDiagnosisService;

    @PostMapping("/diagnose/{sessionId}")
    public ResponseEntity<ApiResponse<AiDiagnosisResponse>> getDiagnosis(
            @PathVariable @NotBlank String sessionId) {

        log.info("Received AI diagnosis request for session: {}", sessionId);

        try {
            AiDiagnosisResponse response = aiDiagnosisService.getDiagnosis(sessionId);
            return ResponseEntity.ok(ApiResponse.success(response, "Chẩn đoán AI thành công"));

        } catch (IllegalArgumentException e) {
            log.warn("Invalid diagnosis request for session: {}, error: {}", sessionId, e.getMessage());
            return ResponseEntity.badRequest()
                    .body(ApiResponse.error(e.getMessage(), 400));

        } catch (Exception e) {
            log.error("Error processing AI diagnosis for session: {}", sessionId, e);
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("Lỗi hệ thống khi thực hiện chẩn đoán", 500));
        }
    }

    @GetMapping("/history")
    public ResponseEntity<ApiResponse<List<AiDiagnosis>>> getDiagnosisHistory() {

        log.info("Getting diagnosis history for current user");

        try {
            List<AiDiagnosis> history = aiDiagnosisService.getUserDiagnosisHistory();
            return ResponseEntity.ok(ApiResponse.success(history));

        } catch (Exception e) {
            log.error("Error getting diagnosis history", e);
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("Lỗi khi lấy lịch sử chẩn đoán", 500));
        }
    }

    @GetMapping("/session/{sessionId}")
    public ResponseEntity<ApiResponse<AiDiagnosis>> getDiagnosisBySession(
            @PathVariable @NotBlank String sessionId) {

        log.info("Getting diagnosis for session: {}", sessionId);

        try {
            AiDiagnosis diagnosis = aiDiagnosisService.getDiagnosisBySession(sessionId);
            return ResponseEntity.ok(ApiResponse.success(diagnosis));

        } catch (IllegalArgumentException e) {
            log.warn("Diagnosis not found for session: {}", sessionId);
            return ResponseEntity.notFound().build();

        } catch (Exception e) {
            log.error("Error getting diagnosis for session: {}", sessionId, e);
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("Lỗi khi lấy kết quả chẩn đoán", 500));
        }
    }
}
