package com.nckh.dia5.controller;

import com.nckh.dia5.dto.blockchain.BlockchainResponse;
import com.nckh.dia5.dto.blockchain.DrugBatch;
import com.nckh.dia5.dto.common.ApiResponse;
import com.nckh.dia5.service.BlockchainService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import java.math.BigInteger;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * REST APIs cho tương tác với blockchain
 */
@Slf4j
@RestController
@RequestMapping("/api/blockchain")
@RequiredArgsConstructor
@Tag(name = "Blockchain", description = "Drug traceability blockchain operations")
public class BlockchainController {

    private final BlockchainService blockchainService;

    /**
     * Health check cho blockchain connection
     */
    @GetMapping("/health")
    @Operation(summary = "Blockchain health check")
    public ResponseEntity<ApiResponse<String>> healthCheck() {
        log.info("🔍 Blockchain health check requested");
        
        BlockchainResponse<String> result = blockchainService.healthCheck();
        
        if (result.isSuccess()) {
            return ResponseEntity.ok(ApiResponse.success(result.getData(), result.getMessage()));
        } else {
            return ResponseEntity.internalServerError()
                .body(ApiResponse.error(result.getMessage()));
        }
    }

    /**
     * Nhà sản xuất tạo lô thuốc mới
     */
    @PostMapping("/manufacturer/batch")
    @Operation(summary = "Create new drug batch", description = "For manufacturers to create new drug batches")
    public CompletableFuture<ResponseEntity<ApiResponse<String>>> createBatch(
            @Valid @RequestBody CreateBatchRequest request) {
        
        log.info("🏭 [API] Create batch request: {}", request.getDrugName());
        
        return blockchainService.createDrugBatch(
                request.getDrugName(),
                request.getActiveIngredient(),
                request.getDosage(),
                request.getManufacturer(),
                request.getRegistrationNumber(),
                request.getQuantity(),
                request.getManufactureDate(),
                request.getExpiryDate(),
                request.getQrCode()
            )
            .thenApply(result -> {
                if (result.isSuccess()) {
                    return ResponseEntity.ok(ApiResponse.success(
                        result.getTransactionHash(), 
                        "Drug batch created successfully"
                    ));
                } else {
                    return ResponseEntity.badRequest()
                        .body(ApiResponse.error(result.getMessage()));
                }
            });
    }

    /**
     * Nhà phân phối tạo shipment
     */
    @PostMapping("/distributor/shipment")
    @Operation(summary = "Create new shipment", description = "For distributors to create shipments")
    public CompletableFuture<ResponseEntity<ApiResponse<String>>> createShipment(
            @Valid @RequestBody CreateShipmentRequest request) {
        
        log.info("🚚 [API] Create shipment request for batch: {}", request.getBatchId());
        
        return blockchainService.createShipment(
                request.getBatchId(),
                request.getPharmacyAddress(),
                request.getQuantity(),
                request.getTrackingNumber()
            )
            .thenApply(result -> {
                if (result.isSuccess()) {
                    return ResponseEntity.ok(ApiResponse.success(
                        result.getTransactionHash(),
                        "Shipment created successfully"
                    ));
                } else {
                    return ResponseEntity.badRequest()
                        .body(ApiResponse.error(result.getMessage()));
                }
            });
    }

    /**
     * Hiệu thuốc nhận hàng
     */
    @PostMapping("/pharmacy/receive/{shipmentId}")
    @Operation(summary = "Receive shipment", description = "For pharmacies to receive shipments")
    public CompletableFuture<ResponseEntity<ApiResponse<String>>> receiveShipment(
            @Parameter(description = "Shipment ID") @PathVariable BigInteger shipmentId) {
        
        log.info("📦 [API] Receive shipment request: {}", shipmentId);
        
        return blockchainService.receiveShipment(shipmentId)
            .thenApply(result -> {
                if (result.isSuccess()) {
                    return ResponseEntity.ok(ApiResponse.success(
                        result.getTransactionHash(),
                        "Shipment received successfully"
                    ));
                } else {
                    return ResponseEntity.badRequest()
                        .body(ApiResponse.error(result.getMessage()));
                }
            });
    }

    /**
     * Xác thực QR code (công khai cho người tiêu dùng)
     */
    @GetMapping("/public/verify/{qrCode}")
    @Operation(summary = "Verify drug authenticity", description = "Public endpoint for consumers to verify drugs")
    public CompletableFuture<ResponseEntity<ApiResponse<DrugBatch>>> verifyDrug(
            @Parameter(description = "QR Code") @PathVariable String qrCode) {
        
        log.info("🔍 [API] Verify drug request: {}", qrCode);
        
        return blockchainService.verifyDrugAuthenticity(qrCode)
            .thenApply(result -> {
                if (result.isSuccess()) {
                    return ResponseEntity.ok(ApiResponse.success(
                        result.getData(),
                        "Drug verification successful"
                    ));
                } else {
                    return ResponseEntity.badRequest()
                        .body(ApiResponse.error(result.getMessage()));
                }
            });
    }

    /**
     * Lấy thông tin chi tiết lô thuốc
     */
    @GetMapping("/batch/{batchId}")
    @Operation(summary = "Get batch details", description = "Get detailed information about a drug batch")
    public CompletableFuture<ResponseEntity<ApiResponse<DrugBatch>>> getBatchDetails(
            @Parameter(description = "Batch ID") @PathVariable BigInteger batchId) {
        
        log.info("📋 [API] Get batch details request: {}", batchId);
        
        return blockchainService.getBatchDetails(batchId)
            .thenApply(result -> {
                if (result.isSuccess()) {
                    return ResponseEntity.ok(ApiResponse.success(
                        result.getData(),
                        "Batch details retrieved successfully"
                    ));
                } else {
                    return ResponseEntity.badRequest()
                        .body(ApiResponse.error(result.getMessage()));
                }
            });
    }

    // DTOs for request bodies
    public static class CreateBatchRequest {
        @NotBlank(message = "Drug name is required")
        private String drugName;
        
        @NotBlank(message = "Active ingredient is required")
        private String activeIngredient;
        
        @NotBlank(message = "Dosage is required")
        private String dosage;
        
        @NotBlank(message = "Manufacturer is required")
        private String manufacturer;
        
        @NotBlank(message = "Registration number is required")
        private String registrationNumber;
        
        @NotNull(message = "Quantity is required")
        @Positive(message = "Quantity must be positive")
        private BigInteger quantity;
        
        @NotNull(message = "Manufacture date is required")
        private LocalDateTime manufactureDate;
        
        @NotNull(message = "Expiry date is required")
        private LocalDateTime expiryDate;
        
        @NotBlank(message = "QR code is required")
        private String qrCode;
        
        // Getters and setters
        public String getDrugName() { return drugName; }
        public void setDrugName(String drugName) { this.drugName = drugName; }
        
        public String getActiveIngredient() { return activeIngredient; }
        public void setActiveIngredient(String activeIngredient) { this.activeIngredient = activeIngredient; }
        
        public String getDosage() { return dosage; }
        public void setDosage(String dosage) { this.dosage = dosage; }
        
        public String getManufacturer() { return manufacturer; }
        public void setManufacturer(String manufacturer) { this.manufacturer = manufacturer; }
        
        public String getRegistrationNumber() { return registrationNumber; }
        public void setRegistrationNumber(String registrationNumber) { this.registrationNumber = registrationNumber; }
        
        public BigInteger getQuantity() { return quantity; }
        public void setQuantity(BigInteger quantity) { this.quantity = quantity; }
        
        public LocalDateTime getManufactureDate() { return manufactureDate; }
        public void setManufactureDate(LocalDateTime manufactureDate) { this.manufactureDate = manufactureDate; }
        
        public LocalDateTime getExpiryDate() { return expiryDate; }
        public void setExpiryDate(LocalDateTime expiryDate) { this.expiryDate = expiryDate; }
        
        public String getQrCode() { return qrCode; }
        public void setQrCode(String qrCode) { this.qrCode = qrCode; }
    }
    
    public static class CreateShipmentRequest {
        @NotNull(message = "Batch ID is required")
        private BigInteger batchId;
        
        @NotBlank(message = "Pharmacy address is required")
        private String pharmacyAddress;
        
        @NotNull(message = "Quantity is required")
        @Positive(message = "Quantity must be positive")
        private BigInteger quantity;
        
        @NotBlank(message = "Tracking number is required")
        private String trackingNumber;
        
        // Getters and setters
        public BigInteger getBatchId() { return batchId; }
        public void setBatchId(BigInteger batchId) { this.batchId = batchId; }
        
        public String getPharmacyAddress() { return pharmacyAddress; }
        public void setPharmacyAddress(String pharmacyAddress) { this.pharmacyAddress = pharmacyAddress; }
        
        public BigInteger getQuantity() { return quantity; }
        public void setQuantity(BigInteger quantity) { this.quantity = quantity; }
        
        public String getTrackingNumber() { return trackingNumber; }
        public void setTrackingNumber(String trackingNumber) { this.trackingNumber = trackingNumber; }
    }
}
