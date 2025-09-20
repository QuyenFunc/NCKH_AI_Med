package com.nckh.dia5.service;

import com.nckh.dia5.dto.blockchain.*;
import com.nckh.dia5.handler.ResourceNotFoundException;
import com.nckh.dia5.model.*;
import com.nckh.dia5.repository.DrugBatchRepository;
import com.nckh.dia5.repository.ShipmentRepository;
import com.nckh.dia5.repository.BlockchainTransactionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.web3j.protocol.core.methods.response.TransactionReceipt;

import java.math.BigInteger;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class DrugTraceabilityService {

    private final DrugBatchRepository drugBatchRepository;
    private final ShipmentRepository shipmentRepository;
    private final BlockchainTransactionRepository blockchainTransactionRepository;
    private final BlockchainService blockchainService;
    private final AuthService authService;

    /**
     * Create a new drug batch
     */
    @Transactional
    public DrugBatchDto createBatch(CreateBatchRequest request) {
        try {
            User currentUser = authService.getCurrentUser();
            String manufacturerAddress = getManufacturerAddress(currentUser);

            // Generate unique batch ID
            BigInteger batchId = generateBatchId();
            
            // Generate QR code
            String qrCode = generateQrCode(batchId, request.getBatchNumber());

            log.info("Creating batch: batchId={}, drugName={}, manufacturer={}", 
                     batchId, request.getDrugName(), request.getManufacturer());

            // Convert expiry date to timestamp
            BigInteger expiryTimestamp = BigInteger.valueOf(
                request.getExpiryDate().toEpochSecond(ZoneOffset.UTC)
            );

            // Create batch on blockchain
            TransactionReceipt receipt = blockchainService.issueBatch(
                request.getDrugName(),
                request.getManufacturer(),
                request.getBatchNumber(),
                BigInteger.valueOf(request.getQuantity()),
                expiryTimestamp,
                request.getStorageConditions()
            ).get();

            // Create local entity
            com.nckh.dia5.model.DrugBatch batch = new com.nckh.dia5.model.DrugBatch();
            batch.setBatchId(batchId);
            batch.setDrugName(request.getDrugName());
            batch.setManufacturer(request.getManufacturer());
            batch.setBatchNumber(request.getBatchNumber());
            batch.setQuantity(request.getQuantity());
            batch.setManufacturerAddress(manufacturerAddress);
            batch.setCurrentOwner(manufacturerAddress);
            batch.setManufactureTimestamp(LocalDateTime.now());
            batch.setExpiryDate(request.getExpiryDate());
            batch.setStorageConditions(request.getStorageConditions());
            batch.setStatus(com.nckh.dia5.model.DrugBatch.BatchStatus.MANUFACTURED);
            batch.setQrCode(qrCode);
            batch.setTransactionHash(receipt.getTransactionHash());
            batch.setBlockNumber(receipt.getBlockNumber());
            batch.setIsSynced(true);

            batch = drugBatchRepository.save(batch);

            // Record blockchain transaction
            recordBlockchainTransaction(receipt, "issueBatch", batch, null);

            log.info("Batch created successfully: id={}, batchId={}", batch.getId(), batchId);
            return mapToDrugBatchDto(batch);

        } catch (Exception e) {
            log.error("Failed to create batch", e);
            throw new RuntimeException("Không thể tạo lô thuốc: " + e.getMessage(), e);
        }
    }

    /**
     * Create a new shipment
     */
    @Transactional
    public ShipmentDto createShipment(CreateShipmentRequest request) {
        try {
            User currentUser = authService.getCurrentUser();
            String fromAddress = getManufacturerAddress(currentUser);

            // Find the batch
            com.nckh.dia5.model.DrugBatch batch = drugBatchRepository.findByBatchId(request.getBatchId())
                    .orElseThrow(() -> new ResourceNotFoundException("Batch", "batchId", request.getBatchId().toString()));

            // Verify ownership
            if (!batch.getCurrentOwner().equals(fromAddress)) {
                throw new IllegalStateException("Bạn không có quyền tạo shipment cho lô này");
            }

            // Verify quantity
            if (request.getQuantity().compareTo(batch.getQuantity()) > 0) {
                throw new IllegalStateException("Số lượng shipment vượt quá số lượng trong lô");
            }

            // Generate shipment ID
            BigInteger shipmentId = generateShipmentId();

            log.info("Creating shipment: shipmentId={}, batchId={}, from={}, to={}, quantity={}", 
                     shipmentId, request.getBatchId(), fromAddress, request.getToAddress(), request.getQuantity());

            // Create shipment on blockchain
            TransactionReceipt receipt = blockchainService.createShipment(
                request.getBatchId(),
                request.getToAddress(),
                BigInteger.valueOf(request.getQuantity())
            ).get();

            // Create local entity
            Shipment shipment = new Shipment();
            shipment.setShipmentId(shipmentId);
            shipment.setFromAddress(fromAddress);
            shipment.setToAddress(request.getToAddress());
            shipment.setQuantity(request.getQuantity());
            shipment.setShipmentTimestamp(LocalDateTime.now());
            shipment.setStatus(Shipment.ShipmentStatus.PENDING);
            shipment.setTrackingInfo(request.getTrackingInfo());
            shipment.setTransactionHash(receipt.getTransactionHash());
            shipment.setBlockNumber(receipt.getBlockNumber());
            shipment.setIsSynced(true);
            shipment.setDrugBatch(batch);

            shipment = shipmentRepository.save(shipment);

            // Update batch status
            batch.setStatus(com.nckh.dia5.model.DrugBatch.BatchStatus.IN_TRANSIT);
            drugBatchRepository.save(batch);

            // Record blockchain transaction
            recordBlockchainTransaction(receipt, "createShipment", batch, shipment);

            log.info("Shipment created successfully: id={}, shipmentId={}", shipment.getId(), shipmentId);
            return mapToShipmentDto(shipment);

        } catch (Exception e) {
            log.error("Failed to create shipment", e);
            throw new RuntimeException("Không thể tạo shipment: " + e.getMessage(), e);
        }
    }

    /**
     * Receive a shipment
     */
    @Transactional
    public ShipmentDto receiveShipment(BigInteger shipmentId) {
        try {
            User currentUser = authService.getCurrentUser();
            String receiverAddress = getManufacturerAddress(currentUser);

            // Find the shipment
            Shipment shipment = shipmentRepository.findByShipmentId(shipmentId)
                    .orElseThrow(() -> new ResourceNotFoundException("Shipment", "shipmentId", shipmentId.toString()));

            // Verify receiver
            if (!shipment.getToAddress().equals(receiverAddress)) {
                throw new IllegalStateException("Bạn không có quyền nhận shipment này");
            }

            log.info("Receiving shipment: shipmentId={}, receiver={}", shipmentId, receiverAddress);

            // Receive shipment on blockchain
            TransactionReceipt receipt = blockchainService.receiveShipment(shipmentId).get();

            // Update shipment status
            shipment.setStatus(Shipment.ShipmentStatus.DELIVERED);
            shipment = shipmentRepository.save(shipment);

            // Update batch owner and status
            com.nckh.dia5.model.DrugBatch batch = shipment.getDrugBatch();
            batch.setCurrentOwner(receiverAddress);
            batch.setStatus(com.nckh.dia5.model.DrugBatch.BatchStatus.DELIVERED);
            drugBatchRepository.save(batch);

            // Record blockchain transaction
            recordBlockchainTransaction(receipt, "receiveShipment", batch, shipment);

            log.info("Shipment received successfully: shipmentId={}", shipmentId);
            return mapToShipmentDto(shipment);

        } catch (Exception e) {
            log.error("Failed to receive shipment", e);
            throw new RuntimeException("Không thể nhận shipment: " + e.getMessage(), e);
        }
    }

    /**
     * Update shipment status
     */
    @Transactional
    public ShipmentDto updateShipmentStatus(UpdateShipmentStatusRequest request) {
        try {
            Shipment shipment = shipmentRepository.findByShipmentId(request.getShipmentId())
                    .orElseThrow(() -> new ResourceNotFoundException("Shipment", "shipmentId", request.getShipmentId().toString()));

            // Update status
            Shipment.ShipmentStatus newStatus = Shipment.ShipmentStatus.valueOf(request.getNewStatus().toUpperCase());
            shipment.setStatus(newStatus);
            
            if (request.getTrackingInfo() != null) {
                shipment.setTrackingInfo(request.getTrackingInfo());
            }

            shipment = shipmentRepository.save(shipment);

            log.info("Shipment status updated: shipmentId={}, newStatus={}", request.getShipmentId(), newStatus);
            return mapToShipmentDto(shipment);

        } catch (Exception e) {
            log.error("Failed to update shipment status", e);
            throw new RuntimeException("Không thể cập nhật trạng thái shipment: " + e.getMessage(), e);
        }
    }

    /**
     * Verify drug authenticity by QR code
     */
    public DrugBatchDto verifyDrug(VerifyDrugRequest request) {
        try {
            com.nckh.dia5.model.DrugBatch batch = drugBatchRepository.findByQrCode(request.getQrCode())
                    .orElseThrow(() -> new ResourceNotFoundException("Drug batch", "qrCode", request.getQrCode()));

            // Verify on blockchain
            boolean isValid = blockchainService.verifyOwnership(batch.getBatchId(), batch.getCurrentOwner()).get();
            
            if (!isValid) {
                throw new IllegalStateException("Thuốc không hợp lệ hoặc đã bị giả mạo");
            }

            log.info("Drug verified successfully: batchId={}, qrCode={}", batch.getBatchId(), request.getQrCode());
            return mapToDrugBatchDto(batch);

        } catch (Exception e) {
            log.error("Failed to verify drug", e);
            throw new RuntimeException("Không thể xác minh thuốc: " + e.getMessage(), e);
        }
    }

    /**
     * Get batch by ID
     */
    public DrugBatchDto getBatch(BigInteger batchId) {
        com.nckh.dia5.model.DrugBatch batch = drugBatchRepository.findByBatchId(batchId)
                .orElseThrow(() -> new ResourceNotFoundException("Batch", "batchId", batchId.toString()));
        return mapToDrugBatchDto(batch);
    }

    /**
     * Get batches by manufacturer
     */
    public List<DrugBatchDto> getBatchesByManufacturer(String manufacturerAddress) {
        List<com.nckh.dia5.model.DrugBatch> batches = drugBatchRepository.findByManufacturerAddress(manufacturerAddress);
        return batches.stream().map(this::mapToDrugBatchDto).collect(Collectors.toList());
    }

    /**
     * Get batches by current owner
     */
    public List<DrugBatchDto> getBatchesByOwner(String ownerAddress) {
        List<com.nckh.dia5.model.DrugBatch> batches = drugBatchRepository.findByCurrentOwner(ownerAddress);
        return batches.stream().map(this::mapToDrugBatchDto).collect(Collectors.toList());
    }

    /**
     * Get shipments by batch
     */
    public List<ShipmentDto> getShipmentsByBatch(BigInteger batchId) {
        com.nckh.dia5.model.DrugBatch batch = drugBatchRepository.findByBatchId(batchId)
                .orElseThrow(() -> new ResourceNotFoundException("Batch", "batchId", batchId.toString()));
        
        List<Shipment> shipments = shipmentRepository.findByDrugBatch(batch);
        return shipments.stream().map(this::mapToShipmentDto).collect(Collectors.toList());
    }

    /**
     * Get transaction history for a batch
     */
    public List<BlockchainTransactionDto> getBatchTransactionHistory(BigInteger batchId) {
        List<BlockchainTransaction> transactions = blockchainTransactionRepository.findByBatchIdOrderByTimestamp(batchId);
        return transactions.stream().map(this::mapToBlockchainTransactionDto).collect(Collectors.toList());
    }

    // Helper methods
    private BigInteger generateBatchId() {
        return new BigInteger(UUID.randomUUID().toString().replace("-", ""), 16).abs();
    }

    private BigInteger generateShipmentId() {
        return new BigInteger(UUID.randomUUID().toString().replace("-", ""), 16).abs();
    }

    private String generateQrCode(BigInteger batchId, String batchNumber) {
        return String.format("NCKH-PHARMA-%s-%s", batchId.toString(16).toUpperCase(), batchNumber);
    }

    private String getManufacturerAddress(User user) {
        // In a real implementation, this would map user to their blockchain address
        // For now, we'll use a placeholder based on user ID
        return "0x" + user.getId().replace("-", "").substring(0, 40);
    }

    private void recordBlockchainTransaction(TransactionReceipt receipt, String functionName, 
                                           com.nckh.dia5.model.DrugBatch batch, Shipment shipment) {
        try {
            BlockchainTransaction transaction = new BlockchainTransaction();
            transaction.setTransactionHash(receipt.getTransactionHash());
            transaction.setBlockNumber(receipt.getBlockNumber());
            transaction.setFromAddress(receipt.getFrom());
            transaction.setToAddress(receipt.getTo());
            transaction.setFunctionName(functionName);
            transaction.setGasUsed(receipt.getGasUsed());
            transaction.setStatus("0x1".equals(receipt.getStatus()) ? 
                                 BlockchainTransaction.TransactionStatus.SUCCESS : 
                                 BlockchainTransaction.TransactionStatus.FAILED);
            transaction.setTimestamp(LocalDateTime.now());
            transaction.setDrugBatch(batch);
            transaction.setShipment(shipment);

            blockchainTransactionRepository.save(transaction);
        } catch (Exception e) {
            log.error("Failed to record blockchain transaction", e);
        }
    }

    // Mapping methods
    private DrugBatchDto mapToDrugBatchDto(com.nckh.dia5.model.DrugBatch batch) {
        return DrugBatchDto.builder()
                .id(batch.getId())
                .batchId(batch.getBatchId())
                .drugName(batch.getDrugName())
                .manufacturer(batch.getManufacturer())
                .batchNumber(batch.getBatchNumber())
                .quantity(batch.getQuantity())
                .manufacturerAddress(batch.getManufacturerAddress())
                .currentOwner(batch.getCurrentOwner())
                .manufactureTimestamp(batch.getManufactureTimestamp())
                .expiryDate(batch.getExpiryDate())
                .storageConditions(batch.getStorageConditions())
                .status(batch.getStatus().name())
                .qrCode(batch.getQrCode())
                .transactionHash(batch.getTransactionHash())
                .blockNumber(batch.getBlockNumber())
                .isSynced(batch.getIsSynced())
                .createdAt(batch.getCreatedAt())
                .updatedAt(batch.getUpdatedAt())
                .build();
    }

    private ShipmentDto mapToShipmentDto(Shipment shipment) {
        return ShipmentDto.builder()
                .id(shipment.getId())
                .shipmentId(shipment.getShipmentId())
                .fromAddress(shipment.getFromAddress())
                .toAddress(shipment.getToAddress())
                .quantity(shipment.getQuantity())
                .shipmentTimestamp(shipment.getShipmentTimestamp())
                .status(shipment.getStatus().name())
                .trackingInfo(shipment.getTrackingInfo())
                .transactionHash(shipment.getTransactionHash())
                .blockNumber(shipment.getBlockNumber())
                .isSynced(shipment.getIsSynced())
                .createdAt(shipment.getCreatedAt())
                .updatedAt(shipment.getUpdatedAt())
                .build();
    }

    private BlockchainTransactionDto mapToBlockchainTransactionDto(BlockchainTransaction transaction) {
        return BlockchainTransactionDto.builder()
                .id(transaction.getId())
                .transactionHash(transaction.getTransactionHash())
                .blockNumber(transaction.getBlockNumber())
                .fromAddress(transaction.getFromAddress())
                .toAddress(transaction.getToAddress())
                .functionName(transaction.getFunctionName())
                .gasUsed(transaction.getGasUsed())
                .gasPrice(transaction.getGasPrice())
                .status(transaction.getStatus().name())
                .inputData(transaction.getInputData())
                .eventLogs(transaction.getEventLogs())
                .errorMessage(transaction.getErrorMessage())
                .timestamp(transaction.getTimestamp())
                .createdAt(transaction.getCreatedAt())
                .drugBatchId(transaction.getDrugBatch() != null ? transaction.getDrugBatch().getId() : null)
                .shipmentId(transaction.getShipment() != null ? transaction.getShipment().getId() : null)
                .build();
    }
}
