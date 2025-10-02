package com.nckh.dia5.service;

import com.nckh.dia5.handler.ResourceNotFoundException;
import com.nckh.dia5.model.*;
import com.nckh.dia5.repository.DistributorInventoryRepository;
import com.nckh.dia5.repository.DrugBatchRepository;
import com.nckh.dia5.repository.PharmaCompanyRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class DistributorInventoryService {

    private final DistributorInventoryRepository inventoryRepository;
    private final DrugBatchRepository drugBatchRepository;
    private final PharmaCompanyRepository pharmaCompanyRepository;

    /**
     * Get all inventory for a distributor
     */
    public List<DistributorInventory> getInventoryByDistributorId(Long distributorId) {
        return inventoryRepository.findByDistributorId(distributorId);
    }

    /**
     * Get inventory by distributor wallet address
     */
    public List<DistributorInventory> getInventoryByWalletAddress(String walletAddress) {
        return inventoryRepository.findByDistributorWalletAddress(walletAddress);
    }

    /**
     * Get low stock items
     */
    public List<DistributorInventory> getLowStockItems(Long distributorId) {
        return inventoryRepository.findLowStockItems(distributorId);
    }

    /**
     * Get expiring soon items
     */
    public List<DistributorInventory> getExpiringSoonItems(Long distributorId) {
        return inventoryRepository.findExpiringSoonItems(distributorId);
    }

    /**
     * Search inventory by drug name
     */
    public List<DistributorInventory> searchByDrugName(Long distributorId, String searchTerm) {
        return inventoryRepository.searchByDrugName(distributorId, searchTerm);
    }

    /**
     * Add or update inventory when receiving shipment
     */
    @Transactional
    public DistributorInventory receiveShipment(Long distributorId, Long batchId, Integer quantity, Shipment shipment) {
        log.info("Receiving shipment to distributor inventory: distributorId={}, batchId={}, quantity={}", 
                distributorId, batchId, quantity);

        // Get distributor
        PharmaCompany distributor = pharmaCompanyRepository.findById(distributorId)
                .orElseThrow(() -> new ResourceNotFoundException("Distributor", "id", distributorId.toString()));

        // Get batch
        DrugBatch batch = drugBatchRepository.findById(batchId)
                .orElseThrow(() -> new ResourceNotFoundException("Batch", "id", batchId.toString()));

        // Check if inventory record exists
        DistributorInventory inventory = inventoryRepository
                .findByDistributorIdAndDrugBatchId(distributorId, batchId)
                .orElse(null);

        if (inventory != null) {
            // Update existing inventory
            log.info("Updating existing inventory record: id={}", inventory.getId());
            inventory.setQuantity(inventory.getQuantity() + quantity);
            inventory.setReceivedShipment(shipment);
            inventory.setReceivedDate(LocalDateTime.now());
            inventory.setUpdatedAt(LocalDateTime.now());
        } else {
            // Create new inventory record
            log.info("Creating new inventory record for distributor");
            inventory = new DistributorInventory();
            inventory.setDistributor(distributor);
            inventory.setDrugBatch(batch);
            inventory.setDrugName(batch.getDrugName());
            inventory.setManufacturer(batch.getManufacturer());
            inventory.setBatchNumber(batch.getBatchNumber());
            inventory.setQuantity(quantity);
            inventory.setManufactureDate(batch.getManufactureTimestamp());
            inventory.setExpiryDate(batch.getExpiryDate());
            inventory.setQrCode(batch.getQrCode());
            inventory.setBlockchainBatchId(batch.getBatchId());
            inventory.setCurrentOwnerAddress(distributor.getWalletAddress());
            inventory.setReceivedFromCompany(shipment.getFromCompany());
            inventory.setReceivedShipment(shipment);
            inventory.setReceivedDate(LocalDateTime.now());
            inventory.setReceivedQuantity(quantity);
        }

        return inventoryRepository.save(inventory);
    }

    /**
     * Reduce inventory when shipping out
     * Returns null if inventory doesn't exist (e.g., batch directly from manufacturer)
     */
    @Transactional
    public DistributorInventory shipOut(Long distributorId, Long batchId, Integer quantity) {
        log.info("Shipping out from distributor inventory: distributorId={}, batchId={}, quantity={}", 
                distributorId, batchId, quantity);

        DistributorInventory inventory = inventoryRepository
                .findByDistributorIdAndDrugBatchId(distributorId, batchId)
                .orElse(null);
        
        if (inventory == null) {
            log.info("No inventory record found - batch might be directly from manufacturer, skipping inventory update");
            return null;
        }

        if (inventory.getAvailableQuantity() < quantity) {
            throw new IllegalStateException("Không đủ số lượng trong kho. Có sẵn: " + inventory.getAvailableQuantity());
        }

        inventory.setQuantity(inventory.getQuantity() - quantity);
        return inventoryRepository.save(inventory);
    }

    /**
     * Reserve quantity for pending shipment
     */
    @Transactional
    public DistributorInventory reserveQuantity(Long distributorId, Long batchId, Integer quantity) {
        DistributorInventory inventory = inventoryRepository
                .findByDistributorIdAndDrugBatchId(distributorId, batchId)
                .orElseThrow(() -> new ResourceNotFoundException("Inventory", "batchId", batchId.toString()));

        if (inventory.getAvailableQuantity() < quantity) {
            throw new IllegalStateException("Không đủ số lượng có thể đặt trước. Có sẵn: " + inventory.getAvailableQuantity());
        }

        inventory.setReservedQuantity(inventory.getReservedQuantity() + quantity);
        return inventoryRepository.save(inventory);
    }

    /**
     * Release reserved quantity
     */
    @Transactional
    public DistributorInventory releaseReservedQuantity(Long distributorId, Long batchId, Integer quantity) {
        DistributorInventory inventory = inventoryRepository
                .findByDistributorIdAndDrugBatchId(distributorId, batchId)
                .orElseThrow(() -> new ResourceNotFoundException("Inventory", "batchId", batchId.toString()));

        inventory.setReservedQuantity(Math.max(0, inventory.getReservedQuantity() - quantity));
        return inventoryRepository.save(inventory);
    }

    /**
     * Get total inventory value
     */
    public Double getTotalInventoryValue(Long distributorId) {
        return inventoryRepository.getTotalInventoryValue(distributorId);
    }
}
