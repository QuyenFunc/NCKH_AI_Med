package com.nckh.dia5.service;

import com.nckh.dia5.dto.blockchain.*;
import com.nckh.dia5.handler.ResourceNotFoundException;
import com.nckh.dia5.model.*;
import com.nckh.dia5.repository.DrugBatchRepository;
import com.nckh.dia5.repository.ShipmentRepository;
import com.nckh.dia5.repository.BlockchainTransactionRepository;
import com.nckh.dia5.repository.PharmaCompanyRepository;
import com.nckh.dia5.util.VietnameseUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.annotation.Propagation;
import org.web3j.protocol.core.methods.response.TransactionReceipt;

import java.math.BigInteger;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class DrugTraceabilityService {

    private final DrugBatchRepository drugBatchRepository;
    private final ShipmentRepository shipmentRepository;
    private final BlockchainTransactionRepository blockchainTransactionRepository;
    private final PharmaCompanyRepository pharmaCompanyRepository;
    private final BlockchainService blockchainService;
    private final ShipmentAdapter shipmentAdapter;
    private final ProductItemService productItemService;
    private final PharmacyInventoryService pharmacyInventoryService;
    private final DistributorInventoryService distributorInventoryService;

    /**
     * Create a new drug batch
     */
    @Transactional
    public DrugBatchDto createBatch(CreateBatchRequest request) {
        try {
            // Validate request
            if (request.getQuantity() == null || request.getQuantity() <= 0) {
                throw new IllegalArgumentException("Số lượng phải lớn hơn 0");
            }
            
            // Use default manufacturer address for development (no auth required)
            String manufacturerAddress = getDefaultManufacturerAddress();

            // Generate unique batch ID
            BigInteger batchId = generateBatchId();
            log.info("=== GENERATED batchId: {} ===", batchId);
            
            // Generate QR code
            String qrCode = generateQrCode(batchId, request.getBatchNumber());

            log.info("Creating batch: batchId={}, drugName={}, manufacturer={}, quantity={}", 
                     batchId, request.getDrugName(), request.getManufacturer(), request.getQuantity());

            // Convert expiry date to timestamp
            BigInteger expiryTimestamp = BigInteger.valueOf(
                request.getExpiryDate().toEpochSecond(ZoneOffset.UTC)
            );

            TransactionReceipt receipt = null;
            boolean blockchainSuccess = false;
            
            try {
                // BỎ DẤU TIẾNG VIỆT trước khi đưa lên blockchain
                String drugNameNoDiacritics = VietnameseUtils.removeVietnameseDiacritics(request.getDrugName());
                String manufacturerNoDiacritics = VietnameseUtils.removeVietnameseDiacritics(request.getManufacturer());
                String storageNoDiacritics = VietnameseUtils.removeVietnameseDiacritics(
                    request.getStorageConditions() != null ? request.getStorageConditions() : "Bao quan o nhiet do phong"
                );
                
                log.info("Sending to blockchain (no diacritics): drug={}, manufacturer={}", 
                         drugNameNoDiacritics, manufacturerNoDiacritics);
                
                // Try to create batch on blockchain with timeout
                receipt = blockchainService.issueBatch(
                    drugNameNoDiacritics,
                    manufacturerNoDiacritics,
                    request.getBatchNumber(),
                    BigInteger.valueOf(request.getQuantity()),
                    expiryTimestamp,
                    storageNoDiacritics
                ).get(10, java.util.concurrent.TimeUnit.SECONDS); // 10 second timeout
                blockchainSuccess = true;
                log.info("Blockchain transaction successful: {}", receipt.getTransactionHash());
            } catch (java.util.concurrent.TimeoutException te) {
                log.warn("Blockchain transaction timed out, proceeding with offline mode");
            } catch (Exception be) {
                log.warn("Blockchain transaction failed: {}, proceeding with offline mode", be.getMessage());
            }

            // Create local entity (regardless of blockchain success)
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
            batch.setStorageConditions(request.getStorageConditions() != null ? request.getStorageConditions() : "Bảo quản ở nhiệt độ phòng");
            batch.setStatus(com.nckh.dia5.model.DrugBatch.BatchStatus.MANUFACTURED);
            batch.setQrCode(qrCode);
            
            if (blockchainSuccess && receipt != null) {
                batch.setTransactionHash(receipt.getTransactionHash());
                // Set block number directly from receipt (BigInteger)
                BigInteger blockNumber = receipt.getBlockNumber();
                batch.setBlockNumber(blockNumber != null ? blockNumber : BigInteger.ONE);
                batch.setIsSynced(true);
            } else {
                // Mark as pending sync for later retry
                batch.setTransactionHash("PENDING_" + System.currentTimeMillis());
                batch.setBlockNumber(BigInteger.ZERO);
                batch.setIsSynced(false);
            }

            log.info("=== BEFORE SAVE: batchId={} ===", batch.getBatchId());
            batch = drugBatchRepository.save(batch);
            log.info("=== AFTER SAVE: id={}, batchId={} ===", batch.getId(), batch.getBatchId());
            drugBatchRepository.flush(); // Force immediate write to DB
            log.info("=== AFTER FLUSH: id={}, batchId={} ===", batch.getId(), batch.getBatchId());

            // Record blockchain transaction if successful
            if (blockchainSuccess && receipt != null) {
                recordBlockchainTransaction(receipt, "issueBatch", batch, null);
            }

            // AUTO-GENERATE PRODUCT ITEMS
            List<ProductItem> generatedItems = List.of();
            try {
                log.info("Auto-generating {} product items for batch {}", request.getQuantity(), batch.getBatchNumber());
                generatedItems = productItemService.autoGenerateItemsForNewBatch(batch, request.getQuantity());
                log.info("Successfully auto-generated {} product items", generatedItems.size());
            } catch (Exception e) {
                log.error("Failed to auto-generate product items: {}", e.getMessage(), e);
                // Don't fail the batch creation if item generation fails
            }

            if (!generatedItems.isEmpty()) {
                List<String> serialNumbers = productItemService.extractSerialNumbers(generatedItems);
                try {
                    log.info("Registering {} serial numbers on blockchain for batch {}", serialNumbers.size(), batch.getBatchNumber());
                    TransactionReceipt registerReceipt = blockchainService.registerSerialNumbers(batch.getBatchId(), serialNumbers)
                            .get(20, java.util.concurrent.TimeUnit.SECONDS);
                    productItemService.markItemsRegistered(generatedItems);
                    batch.setRegisteredSerials((long) serialNumbers.size());
                    drugBatchRepository.save(batch);
                    recordBlockchainTransaction(registerReceipt, "registerSerialNumbers", batch, null);
                    log.info("Serial numbers registered on blockchain successfully");
                } catch (Exception e) {
                    log.error("Failed to register serial numbers on blockchain: {}", e.getMessage(), e);
                }
            }

            log.info("Batch created successfully: id={}, batchId={}, blockchain={}",
                     batch.getId(), batchId, blockchainSuccess ? "synced" : "pending");

            DrugBatchDto dto = mapToDrugBatchDto(batch);
            log.info("=== RETURNING DTO: batchId={} ===", dto.getBatchId());
            return dto;

        } catch (IllegalArgumentException e) {
            log.error("Validation error: {}", e.getMessage());
            throw e;
        } catch (Exception e) {
            log.error("Failed to create batch", e);
            throw new RuntimeException("Không thể tạo lô thuốc: " + e.getMessage(), e);
        }
    }

    /**
     * Create a new shipment
     */
    // Removed @Transactional to avoid rollback issues with triggers
    public ShipmentDto createShipment(CreateShipmentRequest request) {
        String fromAddress = getDefaultManufacturerAddress();
        boolean blockchainSuccess = false;
        TransactionReceipt receipt = null;
        
        try {
            log.info("Starting shipment creation process...");
            
            // Find the batch
            log.info("Looking for batch with ID: {}", request.getBatchId());
            log.info("DEBUG: All batches in DB:");
            drugBatchRepository.flush(); // Ensure all pending changes are written
            List<com.nckh.dia5.model.DrugBatch> allBatches = drugBatchRepository.findAll();
            log.info("DEBUG: Total batches found: {}", allBatches.size());
            for (com.nckh.dia5.model.DrugBatch b : allBatches) {
                log.info("  - DB ID: {}, Batch ID: {}, Number: {}, Owner: {}", 
                    b.getId(), b.getBatchId(), b.getBatchNumber(), b.getCurrentOwner());
            }
            
            com.nckh.dia5.model.DrugBatch batch = drugBatchRepository.findByBatchId(request.getBatchId())
                    .orElseThrow(() -> new ResourceNotFoundException("Batch", "batchId", request.getBatchId().toString()));
            log.info("Found batch: {} with owner: {}", batch.getBatchNumber(), batch.getCurrentOwner());

            // Verify ownership
            log.info("Verifying ownership: fromAddress={}, currentOwner={}", fromAddress, batch.getCurrentOwner());
            if (!batch.getCurrentOwner().equals(fromAddress)) {
                throw new IllegalStateException("Bạn không có quyền tạo shipment cho lô này");
            }

            // Verify quantity
            log.info("Verifying quantity: requested={}, available={}", request.getQuantity(), batch.getQuantity());
            if (request.getQuantity().compareTo(batch.getQuantity()) > 0) {
                throw new IllegalStateException("Số lượng shipment vượt quá số lượng trong lô");
            }

            // Generate shipment ID
            log.info("Generating shipment ID...");
            BigInteger shipmentId = generateShipmentId();
            log.info("Generated shipment ID: {}", shipmentId);

            log.info("Creating shipment: shipmentId={}, batchId={}, from={}, to={}, quantity={}", 
                     shipmentId, request.getBatchId(), fromAddress, request.getToAddress(), request.getQuantity());

            // Generate tracking info if not provided
            String trackingInfo = request.getTrackingInfo();
            if (trackingInfo == null || trackingInfo.trim().isEmpty()) {
                trackingInfo = "SHIPMENT-" + shipmentId;
            }
            
            // Try to create shipment on blockchain
            try {
                receipt = blockchainService.createShipment(
                    request.getBatchId(),
                    request.getToAddress(),
                    BigInteger.valueOf(request.getQuantity()),
                    trackingInfo  // Pass tracking info to blockchain
                ).get();
                blockchainSuccess = true;
                log.info("Shipment created on blockchain successfully with tracking: {}", trackingInfo);
            } catch (Exception e) {
                log.error("Failed to create shipment on blockchain, proceeding with local save", e);
                blockchainSuccess = false;
            }

            // Create local entity using adapter
            log.info("Creating shipment entity using adapter...");
            Shipment shipment;
            if (blockchainSuccess && receipt != null) {
                log.info("Creating shipment with blockchain data");
                shipment = shipmentAdapter.createShipmentFromBlockchain(
                    shipmentId,
                    fromAddress,
                    request.getToAddress(),
                    request.getQuantity(),
                    request.getTrackingInfo(),
                    receipt.getTransactionHash(),
                    receipt.getBlockNumber()
                );
            } else {
                // Fallback: create shipment without blockchain data
                log.info("Creating shipment without blockchain data (fallback mode)");
                shipment = shipmentAdapter.createShipmentFromBlockchain(
                    shipmentId,
                    fromAddress,
                    request.getToAddress(),
                    request.getQuantity(),
                    request.getTrackingInfo(),
                    "PENDING_" + System.currentTimeMillis(),
                    BigInteger.ZERO
                );
            }
            log.info("Shipment entity created successfully");
            
            shipment.setStatus(Shipment.ShipmentStatus.PENDING);
            shipment.setDrugBatch(batch);

            shipment = shipmentRepository.save(shipment);

            // Update batch status
            batch.setStatus(com.nckh.dia5.model.DrugBatch.BatchStatus.IN_TRANSIT);
            drugBatchRepository.save(batch);

            // Record blockchain transaction if successful
            if (blockchainSuccess && receipt != null) {
                recordBlockchainTransaction(receipt, "createShipment", batch, shipment);
            }

            log.info("Shipment created successfully: id={}, shipmentId={}, blockchain={}", 
                     shipment.getId(), shipmentId, blockchainSuccess);
            return mapToShipmentDto(shipment);

        } catch (ResourceNotFoundException | IllegalStateException e) {
            log.error("Validation error creating shipment: {}", e.getMessage());
            throw e;
        } catch (org.springframework.dao.DataIntegrityViolationException e) {
            log.error("Data integrity violation when creating shipment, but returning local saved entity: {}", e.getMessage());
            // Try to persist shipment without triggering problematic triggers by deferring ownership_history
            // Already saved above; return last saved shipment
            List<Shipment> latest = shipmentRepository.findAll();
            Shipment shipment = latest.isEmpty() ? null : latest.get(latest.size() - 1);
            if (shipment == null) {
                throw new RuntimeException("Không thể tạo shipment: dữ liệu không hợp lệ", e);
            }
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
            log.info("Attempting to receive shipment with ID: {}", shipmentId);

            // Try multiple lookup strategies to find the shipment
            Shipment shipment = null;
            
            // Strategy 1: Look by shipment code (SHIP-{id})
            Optional<Shipment> shipmentOpt = shipmentRepository.findByShipmentId(shipmentId);
            if (shipmentOpt.isPresent()) {
                shipment = shipmentOpt.get();
                log.info("Found shipment by shipmentId: {}", shipment.getShipmentCode());
            } else {
                // Strategy 2: Look by blockchain_id in notes JSON field
                log.info("Shipment not found by shipmentId, trying blockchain_id lookup...");
                shipmentOpt = shipmentRepository.findByBlockchainId(shipmentId.toString());
                if (shipmentOpt.isPresent()) {
                    shipment = shipmentOpt.get();
                    log.info("Found shipment by blockchain_id in notes: {}", shipment.getShipmentCode());
                } else {
                    // Strategy 3: Look by database ID as fallback
                    try {
                        shipment = shipmentRepository.findById(shipmentId.longValue()).orElse(null);
                        if (shipment != null) {
                            log.info("Found shipment by database ID: {}", shipment.getShipmentCode());
                        }
                    } catch (Exception e) {
                        log.debug("Failed to find by database ID: {}", e.getMessage());
                    }
                }
            }

            if (shipment == null) {
                throw new ResourceNotFoundException("Shipment", "shipmentId", shipmentId.toString());
            }

            // Get receiver address from shipment (not default manufacturer)
            String receiverAddress = shipment.getToAddress();
            if (receiverAddress == null) {
                // Fallback: extract from notes if available
                if (shipment.getNotes() != null && shipment.getNotes().contains("to_address")) {
                    try {
                        // Simple JSON parsing to extract to_address
                        String notes = shipment.getNotes();
                        int toAddressIndex = notes.indexOf("\"to_address\":");
                        if (toAddressIndex != -1) {
                            int startQuote = notes.indexOf("\"", toAddressIndex + 13);
                            int endQuote = notes.indexOf("\"", startQuote + 1);
                            if (startQuote != -1 && endQuote != -1) {
                                receiverAddress = notes.substring(startQuote + 1, endQuote);
                                log.info("Extracted receiver address from notes: {}", receiverAddress);
                            }
                        }
                    } catch (Exception e) {
                        log.warn("Failed to extract receiver address from notes: {}", e.getMessage());
                    }
                }
                
                if (receiverAddress == null) {
                    receiverAddress = shipment.getToCompany() != null ? shipment.getToCompany().getWalletAddress() : null;
                }
            }

            if (receiverAddress == null) {
                throw new IllegalStateException("Không thể xác định địa chỉ người nhận");
            }

            log.info("Receiving shipment: shipmentCode={}, receiver={}", shipment.getShipmentCode(), receiverAddress);

            // Try to receive shipment on blockchain (but don't fail if it doesn't work)
            try {
                TransactionReceipt receipt = blockchainService.receiveShipment(shipmentId).get();
                // Record blockchain transaction
                recordBlockchainTransaction(receipt, "receiveShipment", shipment.getDrugBatch(), shipment);
                log.info("Shipment received on blockchain successfully");
            } catch (Exception e) {
                log.warn("Failed to receive shipment on blockchain, proceeding with local update: {}", e.getMessage());
            }

            // Update shipment status
            shipment.setStatus(Shipment.ShipmentStatus.DELIVERED);
            shipment.setActualDeliveryDate(LocalDateTime.now());
            shipment = shipmentRepository.save(shipment);

            // Update batch owner and status
            com.nckh.dia5.model.DrugBatch batch = shipment.getDrugBatch();
            if (batch != null) {
                batch.setCurrentOwner(receiverAddress);
                batch.setStatus(com.nckh.dia5.model.DrugBatch.BatchStatus.DELIVERED);
                drugBatchRepository.save(batch);
            }

            // ✅ CRITICAL: Update pharmacy/distributor inventory
            try {
                PharmaCompany receiver = shipment.getToCompany();
                if (receiver != null && batch != null) {
                    if (receiver.getCompanyType() == PharmaCompany.CompanyType.PHARMACY) {
                        // Add to pharmacy_inventory table
                        pharmacyInventoryService.receiveShipment(
                            receiver.getId(),
                            batch.getId(),
                            shipment.getQuantity(),
                            shipment
                        );
                        log.info("✅ Added to pharmacy_inventory: pharmacy={}, batch={}, quantity={}", 
                                receiver.getName(), batch.getBatchNumber(), shipment.getQuantity());
                    } else if (receiver.getCompanyType() == PharmaCompany.CompanyType.DISTRIBUTOR) {
                        // Add to distributor_inventory table
                        distributorInventoryService.receiveShipment(
                            receiver.getId(),
                            batch.getId(),
                            shipment.getQuantity(),
                            shipment
                        );
                        log.info("✅ Added to distributor_inventory: distributor={}, batch={}, quantity={}", 
                                receiver.getName(), batch.getBatchNumber(), shipment.getQuantity());
                    }
                }
            } catch (Exception e) {
                log.error("❌ Failed to update inventory after receiving shipment", e);
                // Don't throw - shipment is already marked as DELIVERED
            }

            log.info("Shipment received successfully: shipmentCode={}", shipment.getShipmentCode());
            return mapToShipmentDto(shipment);

        } catch (Exception e) {
            log.error("Failed to receive shipment", e);
            throw new RuntimeException("Không thể nhận shipment: " + e.getMessage(), e);
        }
    }

    /**
     * Receive a shipment by database ID (fallback method)
     */
    @Transactional
    public ShipmentDto receiveShipmentByDatabaseId(BigInteger databaseId) {
        try {
            log.info("Attempting to receive shipment by database ID: {}", databaseId);

            // Find the shipment by database ID first
            Shipment shipment = shipmentRepository.findById(databaseId.longValue())
                    .orElseThrow(() -> new ResourceNotFoundException("Shipment", "id", databaseId.toString()));

            // Get the receiver address from the shipment (distributor address)
            String receiverAddress = shipment.getToAddress();
            if (receiverAddress == null) {
                // Fallback: extract from notes if available
                if (shipment.getNotes() != null && shipment.getNotes().contains("to_address")) {
                    try {
                        // Simple JSON parsing to extract to_address
                        String notes = shipment.getNotes();
                        int toAddressIndex = notes.indexOf("\"to_address\":");
                        if (toAddressIndex != -1) {
                            int startQuote = notes.indexOf("\"", toAddressIndex + 13);
                            int endQuote = notes.indexOf("\"", startQuote + 1);
                            if (startQuote != -1 && endQuote != -1) {
                                receiverAddress = notes.substring(startQuote + 1, endQuote);
                                log.info("Extracted receiver address from notes: {}", receiverAddress);
                            }
                        }
                    } catch (Exception e) {
                        log.warn("Failed to extract receiver address from notes: {}", e.getMessage());
                    }
                }
                
                if (receiverAddress == null) {
                    receiverAddress = shipment.getToCompany() != null ? shipment.getToCompany().getWalletAddress() : null;
                }
            }
            
            log.info("Receiving shipment by database ID: databaseId={}, shipmentCode={}, receiver={}", 
                     databaseId, shipment.getShipmentCode(), receiverAddress);

            // Skip blockchain transaction for now and just update status
            shipment.setStatus(Shipment.ShipmentStatus.DELIVERED);
            shipment.setActualDeliveryDate(LocalDateTime.now());
            shipment = shipmentRepository.save(shipment);

            // Update batch owner and status
            com.nckh.dia5.model.DrugBatch batch = shipment.getDrugBatch();
            if (batch != null && receiverAddress != null) {
                batch.setCurrentOwner(receiverAddress);
                batch.setStatus(com.nckh.dia5.model.DrugBatch.BatchStatus.DELIVERED);
                drugBatchRepository.save(batch);
            }

            log.info("Shipment received successfully by database ID: {}", shipment.getShipmentCode());
            return mapToShipmentDto(shipment);

        } catch (Exception e) {
            log.error("Failed to receive shipment by database ID", e);
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
    public DrugVerificationResultDto verifyDrug(VerifyDrugRequest request) {
        try {
            com.nckh.dia5.model.DrugBatch batch = drugBatchRepository.findByBatchId(request.getBatchId())
                    .orElseThrow(() -> new ResourceNotFoundException("Drug batch", "batchId", request.getBatchId().toString()));

            ProductItem productItem = productItemService.findByBatchAndSerial(batch, request.getSerialNumber())
                    .orElseThrow(() -> new ResourceNotFoundException("Product item", "serialNumber", request.getSerialNumber()));

            SerialNumberStatusDto serialStatus = blockchainService.getSerialStatus(request.getBatchId(), request.getSerialNumber()).get();

            if (serialStatus == null || !serialStatus.isExists()) {
                throw new IllegalStateException("Serial number không tồn tại trên blockchain");
            }

            if (serialStatus.isRedeemed()) {
                productItemService.markItemRedeemed(productItem, serialStatus.getRedeemedBy(), serialStatus.getRedeemedAt());
                throw new IllegalStateException("Mã QR đã được sử dụng");
            }

            boolean newlyRedeemed = false;

            if (request.isMarkAsSold()) {
                try {
                    TransactionReceipt receipt = blockchainService.redeemSerialNumber(request.getBatchId(), request.getSerialNumber())
                            .get(20, java.util.concurrent.TimeUnit.SECONDS);
                    recordBlockchainTransaction(receipt, "redeemSerialNumber", batch, null);
                    serialStatus = blockchainService.getSerialStatus(request.getBatchId(), request.getSerialNumber()).get();
                    newlyRedeemed = serialStatus != null && serialStatus.isRedeemed();
                } catch (Exception e) {
                    log.error("Failed to redeem serial number on blockchain", e);
                    throw new RuntimeException("Không thể đánh dấu serial đã bán: " + e.getMessage(), e);
                }
            }

            if (newlyRedeemed && serialStatus != null && serialStatus.isRedeemed()) {
                boolean updated = productItemService.markItemRedeemed(productItem, serialStatus.getRedeemedBy(), serialStatus.getRedeemedAt());
                if (updated) {
                    Long redeemedSerials = batch.getRedeemedSerials() != null ? batch.getRedeemedSerials() : 0L;
                    batch.setRedeemedSerials(redeemedSerials + 1);
                    if (batch.getRegisteredSerials() != null
                            && batch.getRedeemedSerials() >= batch.getRegisteredSerials()
                            && batch.getRegisteredSerials() > 0) {
                        batch.setStatus(com.nckh.dia5.model.DrugBatch.BatchStatus.SOLD);
                    }
                    drugBatchRepository.save(batch);
                    try {
                        pharmacyInventoryService.recordSaleForBatch(batch);
                    } catch (Exception e) {
                        log.warn("Failed to update pharmacy inventory after redemption: {}", e.getMessage());
                    }
                }
            }

            log.info("Drug verified successfully: batchId={}, serial={}", batch.getBatchId(), request.getSerialNumber());

            return DrugVerificationResultDto.builder()
                    .batch(mapToDrugBatchDto(batch))
                    .serialNumber(request.getSerialNumber())
                    .serialStatus(serialStatus)
                    .newlyRedeemed(newlyRedeemed && serialStatus != null && serialStatus.isRedeemed())
                    .build();

        } catch (Exception e) {
            log.error("Failed to verify drug", e);
            throw new RuntimeException("Không thể xác minh thuốc: " + e.getMessage(), e);
        }
    }

    /**
     * Get all batches
     */
    public List<DrugBatchDto> getAllBatches() {
        List<com.nckh.dia5.model.DrugBatch> batches = drugBatchRepository.findAll();
        return batches.stream().map(this::mapToDrugBatchDto).collect(Collectors.toList());
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
     * Get shipment by ID
     */
    public ShipmentDto getShipment(BigInteger shipmentId) {
        Shipment shipment = shipmentRepository.findByShipmentId(shipmentId)
                .orElseThrow(() -> new ResourceNotFoundException("Shipment", "shipmentId", shipmentId.toString()));
        return mapToShipmentDto(shipment);
    }

    /**
     * Get shipments by batch
     */
    public List<ShipmentDto> getShipmentsByBatch(BigInteger batchId) {
        try {
            log.info("Getting shipments for batch: {}", batchId);
            
            com.nckh.dia5.model.DrugBatch batch = drugBatchRepository.findByBatchId(batchId)
                    .orElseThrow(() -> new ResourceNotFoundException("Batch not found with batchId: '" + batchId + "'"));
            
            List<Shipment> shipments = shipmentRepository.findByDrugBatch(batch);
            log.info("Found {} shipments for batch {}", shipments.size(), batchId);
            
            return shipments.stream().map(this::mapToShipmentDto).collect(Collectors.toList());
        } catch (ResourceNotFoundException e) {
            log.error("Batch not found: {}", batchId);
            throw e;
        } catch (Exception e) {
            log.error("Error getting shipments for batch {}: {}", batchId, e.getMessage(), e);
            throw new RuntimeException("Failed to get shipments for batch: " + e.getMessage(), e);
        }
    }

    /**
     * Get transaction history for a batch
     */
    public List<BlockchainTransactionDto> getBatchTransactionHistory(BigInteger batchId) {
        List<BlockchainTransaction> transactions = blockchainTransactionRepository.findByBatchIdOrderByTimestamp(batchId);
        return transactions.stream().map(this::mapToBlockchainTransactionDto).collect(Collectors.toList());
    }

    /**
     * Get batches ready for shipment (MANUFACTURED status and owned by manufacturer)
     */
    public List<DrugBatchDto> getBatchesReadyForShipment() {
        String manufacturerAddress = getDefaultManufacturerAddress();
        List<com.nckh.dia5.model.DrugBatch> batches = drugBatchRepository.findByCurrentOwnerAndStatus(
            manufacturerAddress, com.nckh.dia5.model.DrugBatch.BatchStatus.MANUFACTURED);
        return batches.stream().map(this::mapToDrugBatchDto).collect(Collectors.toList());
    }

    /**
     * Get available distributors from pharma_companies table
     */
    public List<DistributorDto> getDistributors() {
        List<PharmaCompany> distributors = pharmaCompanyRepository.findByCompanyTypeAndIsActive(
            PharmaCompany.CompanyType.DISTRIBUTOR, true);
        return distributors.stream().map(this::mapPharmaCompanyToDistributorDto).collect(Collectors.toList());
    }

    /**
     * Get all shipments
     */
    public List<ShipmentDto> getAllShipments() {
        List<Shipment> shipments = shipmentRepository.findAll();
        return shipments.stream().map(this::mapToShipmentDto).collect(Collectors.toList());
    }

    /**
     * Get shipments by manufacturer address
     */
    public List<ShipmentDto> getShipmentsByManufacturer(String manufacturerAddress) {
        List<Shipment> shipments = shipmentRepository.findByFromAddress(manufacturerAddress);
        return shipments.stream().map(this::mapToShipmentDto).collect(Collectors.toList());
    }

    /**
     * Get pending shipments (IN_TRANSIT status)
     */
    public List<ShipmentDto> getPendingShipments() {
        List<Shipment> shipments = shipmentRepository.findByStatus(Shipment.ShipmentStatus.IN_TRANSIT);
        return shipments.stream().map(this::mapToShipmentDto).collect(Collectors.toList());
    }

    /**
     * Get shipments by recipient address
     */
    public List<ShipmentDto> getShipmentsByRecipient(String recipientAddress) {
        List<Shipment> shipments = shipmentRepository.findByToAddress(recipientAddress);
        return shipments.stream().map(this::mapToShipmentDto).collect(Collectors.toList());
    }

    /**
     * Get shipments by sender address (for distributor export management)
     */
    public List<ShipmentDto> getShipmentsBySender(String senderAddress) {
        List<Shipment> shipments = shipmentRepository.findByFromAddress(senderAddress);
        return shipments.stream().map(this::mapToShipmentDto).collect(Collectors.toList());
    }

    // Helper methods
    private BigInteger generateBatchId() {
        // Generate a shorter batch ID that fits in NUMERIC(38,0)
        // Use current timestamp + random number
        long timestamp = System.currentTimeMillis();
        int random = (int) (Math.random() * 10000);
        return BigInteger.valueOf(timestamp * 10000L + random);
    }

    private BigInteger generateShipmentId() {
        // Generate a smaller shipment ID that fits in database
        // Use current timestamp + random number (similar to batchId)
        long timestamp = System.currentTimeMillis();
        int random = (int) (Math.random() * 10000);
        return BigInteger.valueOf(timestamp * 10000L + random);
    }

    private String generateQrCode(BigInteger batchId, String batchNumber) {
        return String.format("NCKH-PHARMA-%s-%s", batchId.toString(16).toUpperCase(), batchNumber);
    }

    private String getManufacturerAddress(User user) {
        // In a real implementation, this would map user to their blockchain address
        // For now, we'll use a placeholder based on user ID
        return "0x" + user.getId().replace("-", "").substring(0, 40);
    }
    
    private String getDefaultManufacturerAddress() {
        // Default manufacturer address for testing
        // This should be replaced with proper user authentication in production
        return "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"; // First Hardhat account
    }


    private void recordBlockchainTransaction(TransactionReceipt receipt, String functionName, 
                                           com.nckh.dia5.model.DrugBatch batch, Shipment shipment) {
        try {
            BlockchainTransaction transaction = new BlockchainTransaction();
            transaction.setTransactionHash(receipt.getTransactionHash());
            // Set block number directly from receipt (BigInteger)
            BigInteger txBlock = receipt.getBlockNumber();
            transaction.setBlockNumber(txBlock != null ? txBlock : BigInteger.ONE);
            transaction.setFromAddress(receipt.getFrom());
            transaction.setToAddress(receipt.getTo());
            transaction.setFunctionName(functionName);
            // Gas used is already BigInteger
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
                .registeredSerials(batch.getRegisteredSerials())
                .redeemedSerials(batch.getRedeemedSerials())
                .createdAt(batch.getCreatedAt())
                .updatedAt(batch.getUpdatedAt())
                .build();
    }

    private ShipmentDto mapToShipmentDto(Shipment shipment) {
        // Extract blockchain data from notes
        Map<String, Object> blockchainData = shipmentAdapter.extractBlockchainData(shipment);
        
        return ShipmentDto.builder()
                .id(shipment.getId())
                .shipmentCode(shipment.getShipmentCode())
                .shipmentId((BigInteger) blockchainData.getOrDefault("shipmentId", BigInteger.ZERO))
                .fromAddress(shipment.getFromCompany() != null ? 
                    shipment.getFromCompany().getWalletAddress() : 
                    (String) blockchainData.get("fromAddress"))
                .toAddress(shipment.getToCompany() != null ? 
                    shipment.getToCompany().getWalletAddress() : 
                    (String) blockchainData.get("toAddress"))
                .quantity(shipment.getQuantity() != null ? shipment.getQuantity().longValue() : 0L)
                .shipmentTimestamp(shipment.getShipmentDate())
                .status(shipment.getStatus().name())
                .trackingInfo((String) blockchainData.getOrDefault("trackingInfo", ""))
                .transactionHash(shipment.getCreateTxHash())
                .blockNumber((BigInteger) blockchainData.get("blockNumber"))
                .isSynced((Boolean) blockchainData.getOrDefault("isSynced", false))
                .createdAt(shipment.getCreatedAt())
                .updatedAt(shipment.getUpdatedAt())
                .drugBatch(shipment.getDrugBatch() != null ? mapToDrugBatchDto(shipment.getDrugBatch()) : null)
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

    private DistributorDto mapPharmaCompanyToDistributorDto(PharmaCompany pharmaCompany) {
        return DistributorDto.builder()
                .id(pharmaCompany.getId())
                .name(pharmaCompany.getName())
                .address(pharmaCompany.getAddress())
                .phone(pharmaCompany.getPhone())
                .email(pharmaCompany.getEmail())
                .walletAddress(pharmaCompany.getWalletAddress())
                .licenseNumber(pharmaCompany.getLicenseNumber())
                .website(null) // PharmaCompany không có website field
                .contactPerson(pharmaCompany.getContactPerson())
                .status(pharmaCompany.getIsActive() ? "ACTIVE" : "INACTIVE")
                .build();
    }
}
