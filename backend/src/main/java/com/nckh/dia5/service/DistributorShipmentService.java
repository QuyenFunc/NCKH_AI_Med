package com.nckh.dia5.service;

import com.nckh.dia5.dto.blockchain.CreateDistributorShipmentRequest;
import com.nckh.dia5.dto.blockchain.ShipmentDto;
import com.nckh.dia5.handler.ResourceNotFoundException;
import com.nckh.dia5.model.DistributorInventory;
import com.nckh.dia5.model.DrugBatch;
import com.nckh.dia5.model.PharmaCompany;
import com.nckh.dia5.model.Shipment;
import com.nckh.dia5.repository.DrugBatchRepository;
import com.nckh.dia5.repository.PharmaCompanyRepository;
import com.nckh.dia5.repository.ShipmentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.web3j.protocol.core.methods.response.TransactionReceipt;

import java.math.BigInteger;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class DistributorShipmentService {

    private final PharmaCompanyRepository pharmaCompanyRepository;
    private final DrugBatchRepository drugBatchRepository;
    private final ShipmentRepository shipmentRepository;
    private final BlockchainService blockchainService;
    private final ShipmentAdapter shipmentAdapter;
    private final DistributorInventoryService distributorInventoryService;

    @Transactional
    public ShipmentDto createShipmentToPharmacy(CreateDistributorShipmentRequest request) {
        try {
            log.info("Starting distributor shipment creation...");
            
            // 1. Find pharmacy by ID and get wallet address
            PharmaCompany pharmacy = pharmaCompanyRepository.findById(request.getPharmacyId())
                    .orElseThrow(() -> new ResourceNotFoundException("Pharmacy", "id", request.getPharmacyId().toString()));
            
            if (pharmacy.getCompanyType() != PharmaCompany.CompanyType.PHARMACY) {
                throw new IllegalArgumentException("Company với ID " + request.getPharmacyId() + " không phải là hiệu thuốc");
            }
            
            if (pharmacy.getWalletAddress() == null || pharmacy.getWalletAddress().trim().isEmpty()) {
                throw new IllegalStateException("Hiệu thuốc chưa có địa chỉ ví blockchain");
            }
            
            log.info("Found pharmacy: {} with wallet address: {}", pharmacy.getName(), pharmacy.getWalletAddress());
            
            // 2. Find batch
            DrugBatch batch = drugBatchRepository.findByBatchId(request.getBatchId())
                    .orElseThrow(() -> new ResourceNotFoundException("Batch", "batchId", request.getBatchId().toString()));
            
            log.info("Found batch: {} with total quantity: {}", batch.getBatchNumber(), batch.getQuantity());
            
            // 3. Verify quantity - check distributor inventory instead of batch
            // Note: We'll verify actual available quantity when calling distributorInventoryService.shipOut()
            
            // 4. Get distributor address (current owner)
            String distributorAddress = batch.getCurrentOwner();
            log.info("Distributor address (current owner): {}", distributorAddress);
            
            // 5. Generate tracking number if not provided
            String trackingNumber = request.getTrackingNumber();
            if (trackingNumber == null || trackingNumber.trim().isEmpty()) {
                trackingNumber = "TRK-" + System.currentTimeMillis();
            }
            
            // 6. Try to create shipment on blockchain
            boolean blockchainSuccess = false;
            TransactionReceipt receipt = null;
            BigInteger shipmentId = BigInteger.valueOf(System.currentTimeMillis());
            
            try {
                receipt = blockchainService.createShipment(
                    request.getBatchId(),
                    pharmacy.getWalletAddress(),
                    BigInteger.valueOf(request.getQuantity())
                ).get();
                blockchainSuccess = true;
                log.info("Shipment created on blockchain successfully. TX: {}", receipt.getTransactionHash());
            } catch (Exception e) {
                log.warn("Failed to create shipment on blockchain, proceeding with local save: {}", e.getMessage());
            }
            
            // 7. Create shipment entity
            Shipment shipment;
            if (blockchainSuccess && receipt != null) {
                shipment = shipmentAdapter.createShipmentFromBlockchain(
                    shipmentId,
                    distributorAddress,
                    pharmacy.getWalletAddress(),
                    request.getQuantity(),
                    trackingNumber,
                    receipt.getTransactionHash(),
                    receipt.getBlockNumber()
                );
            } else {
                shipment = shipmentAdapter.createShipmentFromBlockchain(
                    shipmentId,
                    distributorAddress,
                    pharmacy.getWalletAddress(),
                    request.getQuantity(),
                    trackingNumber,
                    "PENDING_" + System.currentTimeMillis(),
                    BigInteger.ZERO
                );
            }
            
            // 8. Set additional information
            shipment.setStatus(Shipment.ShipmentStatus.IN_TRANSIT);
            shipment.setDrugBatch(batch);
            shipment.setShipmentDate(LocalDateTime.now());
            shipment.setExpectedDeliveryDate(LocalDateTime.now().plusDays(2));
            
            // 9. Build notes with additional info
            Map<String, Object> additionalInfo = new HashMap<>();
            additionalInfo.put("tracking_number", trackingNumber);
            additionalInfo.put("driver_name", request.getDriverName());
            additionalInfo.put("driver_phone", request.getDriverPhone());
            additionalInfo.put("transport_method", request.getTransportMethod());
            additionalInfo.put("user_notes", request.getNotes());
            additionalInfo.put("pharmacy_name", pharmacy.getName());
            additionalInfo.put("pharmacy_address", pharmacy.getAddress());
            
            String currentNotes = shipment.getNotes() != null ? shipment.getNotes() : "{}";
            // Merge with existing notes (which contains blockchain data)
            shipment.setNotes(currentNotes.replace("}", ", \"shipment_info\": " + toJson(additionalInfo) + "}"));
            
            // 10. DO NOT update batch quantity - batch quantity represents total manufactured
            // Individual inventories (distributor_inventory, pharmacy_inventory) track actual quantities
            // batch.setQuantity(batch.getQuantity() - request.getQuantity());
            // drugBatchRepository.save(batch);
            
            // 11. Update distributor inventory (reduce quantity) if exists
            // NOTE: If distributor doesn't have inventory record, we allow shipment anyway
            // This handles the case where distributor receives batch directly from blockchain
            Long distributorId = pharmaCompanyRepository.findByWalletAddress(distributorAddress)
                    .map(PharmaCompany::getId)
                    .orElse(null);
            
            if (distributorId != null) {
                // Try to ship out from inventory - this will check available quantity
                DistributorInventory inventoryResult = distributorInventoryService.shipOut(
                    distributorId, batch.getId(), request.getQuantity().intValue());
                
                if (inventoryResult != null) {
                    log.info("Distributor inventory updated successfully");
                } else {
                    // No inventory record - just log and continue
                    // The shipment can proceed (batch ownership verification already done via current_owner)
                    log.info("No distributor inventory record - proceeding with shipment (batch owned directly)");
                }
            } else {
                log.warn("Could not find distributor with wallet address: {}", distributorAddress);
            }
            
            // 12. Save shipment
            Shipment savedShipment = shipmentRepository.save(shipment);
            log.info("Shipment saved successfully with ID: {}", savedShipment.getId());
            
            // 13. Convert to DTO and return
            return convertToDto(savedShipment, batch, pharmacy);
            
        } catch (Exception e) {
            log.error("Failed to create distributor shipment", e);
            throw new RuntimeException("Không thể tạo phiếu xuất kho: " + e.getMessage(), e);
        }
    }

    public List<ShipmentDto> getAllShipments() {
        List<Shipment> shipments = shipmentRepository.findAll();
        return shipments.stream()
                .map(s -> convertToDto(s, s.getDrugBatch(), s.getToCompany()))
                .collect(Collectors.toList());
    }

    public ShipmentDto getShipmentById(Long id) {
        Shipment shipment = shipmentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Shipment", "id", id.toString()));
        return convertToDto(shipment, shipment.getDrugBatch(), shipment.getToCompany());
    }

    private ShipmentDto convertToDto(Shipment shipment, DrugBatch batch, PharmaCompany pharmacy) {
        return ShipmentDto.builder()
                .id(shipment.getId())
                .shipmentCode(shipment.getShipmentCode())
                .shipmentId(shipment.getShipmentId() != null ? shipment.getShipmentId() : BigInteger.valueOf(shipment.getId()))
                .fromAddress(shipment.getFromCompany() != null ? shipment.getFromCompany().getWalletAddress() : null)
                .toAddress(pharmacy != null ? pharmacy.getWalletAddress() : null)
                .quantity(shipment.getQuantity() != null ? shipment.getQuantity().longValue() : 0L)
                .shipmentTimestamp(shipment.getShipmentDate() != null ? shipment.getShipmentDate() : shipment.getCreatedAt())
                .status(shipment.getStatus().name())
                .trackingInfo(shipment.getNotes())
                .transactionHash(shipment.getCreateTxHash())
                .blockNumber(shipment.getBlockNumber())
                .isSynced(shipment.getIsSynced())
                .createdAt(shipment.getCreatedAt())
                .updatedAt(shipment.getUpdatedAt())
                .build();
    }

    private String toJson(Map<String, Object> map) {
        StringBuilder json = new StringBuilder("{");
        map.forEach((key, value) -> {
            if (value != null) {
                json.append("\"").append(key).append("\": \"").append(value.toString()).append("\", ");
            }
        });
        if (json.length() > 1) {
            json.setLength(json.length() - 2); // Remove trailing comma
        }
        json.append("}");
        return json.toString();
    }
}
