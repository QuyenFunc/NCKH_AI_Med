package com.nckh.dia5.dto.blockchain;

import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.databind.ser.std.ToStringSerializer;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigInteger;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class VerifyDrugRequest {

    @NotNull(message = "Mã QR không được để trống")
    @Size(min = 1, max = 1000, message = "Mã QR phải từ 1 đến 1000 ký tự")
    private String qrCode;

    @NotNull(message = "Batch ID không được để trống")
    @JsonSerialize(using = ToStringSerializer.class)
    private BigInteger batchId;

    @NotNull(message = "Serial number không được để trống")
    @Size(min = 1, max = 255, message = "Serial number phải từ 1 đến 255 ký tự")
    private String serialNumber;

    @Builder.Default
    private boolean markAsSold = true;
}
