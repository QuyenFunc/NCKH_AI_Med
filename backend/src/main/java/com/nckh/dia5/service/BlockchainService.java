package com.nckh.dia5.service;

import com.nckh.dia5.dto.blockchain.BlockchainResponse;
import com.nckh.dia5.dto.blockchain.DrugBatch;
import com.nckh.dia5.dto.blockchain.DrugShipment;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigInteger;
import java.time.LocalDateTime;
import java.util.concurrent.CompletableFuture;

/**
 * Service chính để tương tác với blockchain
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class BlockchainService {

    private final PharmaLedgerContract pharmaLedgerContract;

    /**
     * Nhà sản xuất tạo lô thuốc mới
     */
    public CompletableFuture<BlockchainResponse<String>> createDrugBatch(
            String drugName,
            String activeIngredient,
            String dosage,
            String manufacturer,
            String registrationNumber,
            BigInteger quantity,
            LocalDateTime manufactureDate,
            LocalDateTime expiryDate,
            String qrCode) {
        
        log.info("🏭 [MANUFACTURER] Creating new drug batch: {}", drugName);
        
        return pharmaLedgerContract.issueBatch(
                DrugBatch.DrugInfo.builder()
                    .name(drugName)
                    .activeIngredient(activeIngredient)
                    .dosage(dosage)
                    .manufacturer(manufacturer)
                    .registrationNumber(registrationNumber)
                    .build(),
                quantity,
                manufactureDate,
                expiryDate,
                qrCode
            )
            .thenApply(txHash -> {
                log.info("✅ Drug batch created successfully. TX: {}", txHash);
                return BlockchainResponse.success(txHash, txHash);
            })
            .exceptionally(ex -> {
                log.error("❌ Failed to create drug batch: {}", ex.getMessage());
                return BlockchainResponse.error("Failed to create drug batch: " + ex.getMessage());
            });
    }

    /**
     * Nhà phân phối tạo shipment mới
     */
    public CompletableFuture<BlockchainResponse<String>> createShipment(
            BigInteger batchId,
            String pharmacyAddress,
            BigInteger quantity,
            String trackingNumber) {
        
        log.info("🚚 [DISTRIBUTOR] Creating shipment for batch {} to pharmacy {}", batchId, pharmacyAddress);
        
        return pharmaLedgerContract.createShipment(batchId, pharmacyAddress, quantity, trackingNumber)
            .thenApply(txHash -> {
                log.info("✅ Shipment created successfully. TX: {}", txHash);
                return BlockchainResponse.success(txHash, txHash);
            })
            .exceptionally(ex -> {
                log.error("❌ Failed to create shipment: {}", ex.getMessage());
                return BlockchainResponse.error("Failed to create shipment: " + ex.getMessage());
            });
    }

    /**
     * Hiệu thuốc nhận hàng
     */
    public CompletableFuture<BlockchainResponse<String>> receiveShipment(BigInteger shipmentId) {
        log.info("📦 [PHARMACY] Receiving shipment: {}", shipmentId);
        
        return pharmaLedgerContract.receiveShipment(shipmentId)
            .thenApply(txHash -> {
                log.info("✅ Shipment received successfully. TX: {}", txHash);
                return BlockchainResponse.success(txHash, txHash);
            })
            .exceptionally(ex -> {
                log.error("❌ Failed to receive shipment: {}", ex.getMessage());
                return BlockchainResponse.error("Failed to receive shipment: " + ex.getMessage());
            });
    }

    /**
     * Xác thực QR code (cho người tiêu dùng)
     */
    public CompletableFuture<BlockchainResponse<DrugBatch>> verifyDrugAuthenticity(String qrCode) {
        log.info("🔍 [CONSUMER] Verifying drug authenticity with QR: {}", qrCode);
        
        return pharmaLedgerContract.verifyQRCode(qrCode)
            .thenApply(batch -> {
                log.info("✅ Drug verification successful for QR: {}", qrCode);
                return BlockchainResponse.success(batch);
            })
            .exceptionally(ex -> {
                log.error("❌ Failed to verify drug: {}", ex.getMessage());
                return BlockchainResponse.error("Failed to verify drug: " + ex.getMessage());
            });
    }

    /**
     * Lấy thông tin chi tiết lô thuốc
     */
    public CompletableFuture<BlockchainResponse<DrugBatch>> getBatchDetails(BigInteger batchId) {
        log.info("📋 Getting batch details: {}", batchId);
        
        return pharmaLedgerContract.getBatchInfo(batchId)
            .thenApply(batch -> {
                log.info("✅ Batch details retrieved successfully: {}", batchId);
                return BlockchainResponse.success(batch);
            })
            .exceptionally(ex -> {
                log.error("❌ Failed to get batch details: {}", ex.getMessage());
                return BlockchainResponse.error("Failed to get batch details: " + ex.getMessage());
            });
    }

    /**
     * Health check cho blockchain connection
     */
    public BlockchainResponse<String> healthCheck() {
        try {
            // Simple check to see if we can connect to blockchain
            log.info("🔍 Checking blockchain connection...");
            
            // TODO: Add actual health check logic
            
            return BlockchainResponse.success("Blockchain connection is healthy");
        } catch (Exception e) {
            log.error("❌ Blockchain health check failed: {}", e.getMessage());
            return BlockchainResponse.error("Blockchain connection failed: " + e.getMessage());
        }
    }
}
