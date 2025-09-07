package com.nckh.dia5.dto.medical;

import com.nckh.dia5.model.UserSymptomReport;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SymptomReportRequest {

    private String sessionId;

    @NotNull(message = "ID triệu chứng không được để trống")
    private Integer symptomId;

    @Min(value = 1, message = "Mức độ nghiêm trọng phải từ 1-10")
    @Max(value = 10, message = "Mức độ nghiêm trọng phải từ 1-10")
    private Integer severity;

    @Min(value = 0, message = "Thời gian kéo dài không được âm")
    private Integer durationHours;

    private UserSymptomReport.Frequency frequency;

    private List<String> triggers;

    private List<String> associatedSymptoms;

    private String locationBodyPart;

    private String qualityDescription;

    private UserSymptomReport.OnsetType onsetType;
}
