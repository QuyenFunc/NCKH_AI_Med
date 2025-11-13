package com.nckh.dia5.service;

import com.nckh.dia5.model.DrugBatch;
import com.nckh.dia5.model.ProductItem;
import com.nckh.dia5.repository.ProductItemRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class ProductItemService {

    private final ProductItemRepository productItemRepository;

    /**
     * Tự động sinh danh sách hộp thuốc cho lô mới
     */
    @Transactional
    public List<ProductItem> autoGenerateItemsForNewBatch(DrugBatch batch, long quantity) {
        List<ProductItem> items = new ArrayList<>();

        for (long i = 0; i < quantity; i++) {
            String serialNumber = generateSerialNumber(batch, i + 1);

            if (productItemRepository.findBySerialNumber(serialNumber).isPresent()) {
                log.warn("Serial number {} already exists, skipping", serialNumber);
                continue;
            }

            String qrPayload = buildQrPayload(batch, serialNumber);

            ProductItem item = ProductItem.builder()
                    .drugBatch(batch)
                    .serialNumber(serialNumber)
                    .qrCode(qrPayload)
                    .status(ProductItem.ProductItemStatus.CREATED)
                    .blockchainRegistered(false)
                    .blockchainRedeemed(false)
                    .build();

            items.add(item);
        }

        if (items.isEmpty()) {
            return List.of();
        }

        List<ProductItem> savedItems = productItemRepository.saveAll(items);
        log.info("Generated {} product items for batch {}", savedItems.size(), batch.getBatchNumber());
        return savedItems;
    }

    /**
     * Đánh dấu các hộp đã được đồng bộ serial lên blockchain
     */
    @Transactional
    public void markItemsRegistered(List<ProductItem> items) {
        for (ProductItem item : items) {
            item.setStatus(ProductItem.ProductItemStatus.REGISTERED);
            item.setBlockchainRegistered(true);
        }
        productItemRepository.saveAll(items);
    }

    /**
     * Đánh dấu hộp đã được bán/đổi trả trên blockchain
     *
     * @return true nếu trạng thái thay đổi
     */
    @Transactional
    public boolean markItemRedeemed(ProductItem item, String redeemedByAddress, Long redeemedAtEpochSeconds) {
        boolean statusChanged = item.getStatus() != ProductItem.ProductItemStatus.REDEEMED
                || !Boolean.TRUE.equals(item.getBlockchainRedeemed());

        item.setStatus(ProductItem.ProductItemStatus.REDEEMED);
        item.setBlockchainRedeemed(true);
        item.setRedeemedByAddress(redeemedByAddress);

        if (redeemedAtEpochSeconds != null && redeemedAtEpochSeconds > 0) {
            LocalDateTime redeemedAt = LocalDateTime.ofInstant(
                    Instant.ofEpochSecond(redeemedAtEpochSeconds), ZoneOffset.UTC);
            item.setRedeemedAt(redeemedAt);
        } else {
            item.setRedeemedAt(LocalDateTime.now());
        }

        productItemRepository.save(item);
        return statusChanged;
    }

    public Optional<ProductItem> findByBatchAndSerial(DrugBatch batch, String serialNumber) {
        return productItemRepository.findByDrugBatchAndSerialNumber(batch, serialNumber);
    }

    public Optional<ProductItem> findBySerial(String serialNumber) {
        return productItemRepository.findBySerialNumber(serialNumber);
    }

    public long countAllItems() {
        return productItemRepository.count();
    }

    public long countBlockchainSyncedItems() {
        return productItemRepository.countByBlockchainRegisteredTrue();
    }

    public Map<String, Long> getStatusCounts() {
        Map<String, Long> counts = new HashMap<>();
        for (ProductItem.ProductItemStatus status : ProductItem.ProductItemStatus.values()) {
            counts.put(status.name(), productItemRepository.countByStatus(status));
        }
        return counts;
    }

    public List<String> extractSerialNumbers(List<ProductItem> items) {
        return items.stream()
                .map(ProductItem::getSerialNumber)
                .collect(Collectors.toList());
    }

    private String generateSerialNumber(DrugBatch batch, long index) {
        return String.format("%s-%s-%05d",
                batch.getBatchId() != null ? batch.getBatchId().toString() : "BATCH",
                batch.getBatchNumber(),
                index);
    }

    private String buildQrPayload(DrugBatch batch, String serialNumber) {
        return String.format("{\"batchId\":\"%s\",\"serialNumber\":\"%s\"}",
                batch.getBatchId() != null ? batch.getBatchId().toString() : "",
                serialNumber);
    }
}
