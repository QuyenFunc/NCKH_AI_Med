package com.nckh.dia5.dto.blockchain;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import jakarta.validation.constraints.Positive;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigInteger;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreateShipmentRequest {

    @NotNull(message = "Batch ID không được để trống")
    private BigInteger batchId;

    @NotNull(message = "Địa chỉ nhận không được để trống")
    @Size(min = 42, max = 42, message = "Địa chỉ nhận phải có đúng 42 ký tự")
    private String toAddress;

    @NotNull(message = "Số lượng không được để trống")
    @Positive(message = "Số lượng phải lớn hơn 0")
    private Long quantity;

    @Size(max = 1000, message = "Thông tin theo dõi không được vượt quá 1000 ký tự")
    private String trackingInfo;
}
