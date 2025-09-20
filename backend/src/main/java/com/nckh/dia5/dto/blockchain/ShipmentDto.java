package com.nckh.dia5.dto.blockchain;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import jakarta.validation.constraints.Positive;
import java.math.BigInteger;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ShipmentDto {

    private Long id;

    @NotNull(message = "Shipment ID không được để trống")
    private BigInteger shipmentId;

    @NotNull(message = "Địa chỉ gửi không được để trống")
    @Size(min = 42, max = 42, message = "Địa chỉ gửi phải có đúng 42 ký tự")
    private String fromAddress;

    @NotNull(message = "Địa chỉ nhận không được để trống")
    @Size(min = 42, max = 42, message = "Địa chỉ nhận phải có đúng 42 ký tự")
    private String toAddress;

    @NotNull(message = "Số lượng không được để trống")
    @Positive(message = "Số lượng phải lớn hơn 0")
    private Long quantity;

    @NotNull(message = "Thời gian gửi hàng không được để trống")
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime shipmentTimestamp;

    @NotNull(message = "Trạng thái không được để trống")
    private String status;

    @Size(max = 1000, message = "Thông tin theo dõi không được vượt quá 1000 ký tự")
    private String trackingInfo;

    @Size(max = 66, message = "Hash giao dịch không được vượt quá 66 ký tự")
    private String transactionHash;

    private BigInteger blockNumber;

    private Boolean isSynced;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime createdAt;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime updatedAt;

    private DrugBatchDto drugBatch;
    private List<BlockchainTransactionDto> transactions;
}
